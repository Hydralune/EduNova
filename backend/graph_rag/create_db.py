import os
import sys
import argparse
import hashlib
import json
import networkx as nx
from tqdm.asyncio import tqdm
from typing import List, Callable, Optional
import logging
import asyncio
import subprocess
import tempfile
import shutil
import uuid
import requests
import shutil as _shutil
import time
import traceback

# 禁用 ChromaDB telemetry 以防止崩溃
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# This is needed if embedding_util is in the parent directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    UnstructuredFileLoader,
    Docx2txtLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.rag.embedding_util import get_embedding
from backend.rag.knowledge_graph import build_knowledge_graph

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurable parameters via environment variables ---
# Larger chunk reduces number of LLM calls (speed ↑) but increases prompt size.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))  # 减小到300字符，确保不超过512 tokens限制
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # 相应减小overlap
# Max parallel API calls (respect provider's rate-limit)
CONCURRENCY_LIMIT = int(os.getenv("LLM_CONCURRENCY", "8"))

# --- LLM and Parser Initialization ---
def get_llm():
    """Initializes and returns the LLM."""
    # Fetch credentials from generic environment variables so that any provider compatible with
    # the OpenAI API can be plugged in by simply editing the .env file (no code changes needed).
    api_key = os.getenv("LLM_API_KEY", "sk-dfthbfklqzgxhhrfiwukmgfakpcfuletjjvapquirwwcuteh")
    base_url = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("LLM_MODEL", "Qwen/Qwen3-8B")

    if not api_key:
        raise ValueError("LLM_API_KEY not found in .env file.")
    if not base_url:
        raise ValueError("LLM_API_BASE not found in .env file.")
    if not model_name:
        raise ValueError("LLM_MODEL not found in .env file.")
    return ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=base_url,
        model_name=model_name,
        temperature=0,
        max_retries=3
    )

def get_graph_extraction_chain(llm):
    """Creates a chain for extracting entities and relationships."""
    prompt = ChatPromptTemplate.from_template("""
From the following text, extract key entities (like concepts, people, technologies) and the relationships between them.
Format the output as a JSON object with two keys: 'entities' and 'relationships'.
- 'entities' should be a list of objects, each with 'name' (the entity's name) and 'type' (e.g., 'Concept', 'Person', 'Technology').
- 'relationships' should be a list of objects, each with 'source' (source entity name), 'target' (target entity name), and 'label' (a description of the relationship).
The entity names in relationships must exactly match the names in the entities list.

Text:
---
{chunk_text}
---
    """)
    return prompt | llm | JsonOutputParser()

# --- Embedding Function Definition ---
class EmbeddingFunction:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.batch_size = 5  # 进一步减小批处理大小，避免API限制
        self.logger = logging.getLogger(__name__)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using Silicon Flow API with correct dimension"""
        try:
            from backend.rag.embedding_util import get_embedding
            
            # 过滤空文本
            texts = [text.strip() for text in texts if text and text.strip()]
            if not texts:
                self.logger.warning("没有有效的文本进行向量化")
                return [[0.0] * 1024]
            
            # 分批处理
            batch_size = self.batch_size
            all_embeddings = []
            
            self.logger.info(f"开始向量化 {len(texts)} 个文本，批处理大小: {batch_size}")
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size
                
                self.logger.info(f"处理批次 {batch_num}/{total_batches}: {len(batch)} 个文本")
                
                try:
                    result = get_embedding(batch, max_retries=3)
                    
                    if 'data' in result and result['data']:
                        batch_embeddings = [item['embedding'] for item in result['data']]
                        all_embeddings.extend(batch_embeddings)
                        self.logger.info(f"批次 {batch_num} 向量化成功: {len(batch_embeddings)} 个embedding")
                    else:
                        self.logger.error(f"批次 {batch_num} API返回格式错误")
                        # 为这个批次创建占位符embedding
                        batch_embeddings = [[0.0] * 1024 for _ in batch]
                        all_embeddings.extend(batch_embeddings)
                    
                    # 更新进度
                    if self.progress_callback:
                        progress = min(100, (i + len(batch)) / len(texts) * 100)
                        self.progress_callback(progress)
                        
                except Exception as batch_error:
                    self.logger.error(f"批次 {batch_num} 向量化失败: {batch_error}")
                    # 为这个批次创建占位符embedding
                    batch_embeddings = [[0.0] * 1024 for _ in batch]
                    all_embeddings.extend(batch_embeddings)
                    
                    # 继续处理下一个批次，而不是完全失败
                    continue
            
            # 验证维度（siliconflow BAAI/bge-large-zh-v1.5 = 1024维）
            embedding_dimension = 1024
            if all_embeddings:
                for i, embedding in enumerate(all_embeddings):
                    if len(embedding) != embedding_dimension:
                        self.logger.error(f"第 {i} 个embedding维度不匹配: 期望{embedding_dimension}，实际{len(embedding)}")
                        # 修正维度
                        if len(embedding) > embedding_dimension:
                            all_embeddings[i] = embedding[:embedding_dimension]
                        else:
                            all_embeddings[i] = embedding + [0.0] * (embedding_dimension - len(embedding))
            
            self.logger.info(f"向量化完成: {len(all_embeddings)} 个embedding")
            return all_embeddings
            
        except Exception as e:
            self.logger.error(f"向量化过程中出现严重错误: {e}")
            # 返回占位符embedding，确保不会崩溃
            embedding_dimension = 1024
            return [[0.0] * embedding_dimension] * len(texts)

    def embed_query(self, text: str) -> List[float]:
        """用于查询的embedding方法"""
        try:
            from backend.rag.embedding_util import get_embedding
            
            if not text or not text.strip():
                self.logger.warning("查询文本为空")
                return [0.0] * 1024
            
            result = get_embedding([text], max_retries=3)
            if 'data' in result and result['data']:
                embedding = result['data'][0]['embedding']
                # 验证维度
                if len(embedding) != 1024:
                    self.logger.error(f"查询embedding维度不匹配: 期望1024，实际{len(embedding)}")
                    if len(embedding) > 1024:
                        embedding = embedding[:1024]
                    else:
                        embedding = embedding + [0.0] * (1024 - len(embedding))
                return embedding
            else:
                self.logger.error("查询embedding API返回格式错误")
                return [0.0] * 1024
        except Exception as e:
            self.logger.error(f"查询embedding失败: {e}")
            return [0.0] * 1024

# --- Helper Functions ---
def get_or_create_course_db_path(course_id: str, base_persist_dir: str = "backend/uploads/knowledge_base") -> str:
    persist_dir = os.path.join(base_persist_dir, course_id)
    os.makedirs(persist_dir, exist_ok=True)
    return persist_dir

def get_file_hash(file_path: str) -> str:
    """获取文件的MD5哈希值"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)  # 64kb chunks
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def load_processed_files_metadata(metadata_file: str) -> dict:
    """加载已处理文件的元数据"""
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_processed_files_metadata(metadata_file: str, data: dict):
    """保存已处理文件的元数据"""
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def process_chunk_for_graph(chunk, graph_extraction_chain):
    """Asynchronously processes a single chunk to extract graph data."""
    chunk_id = chunk.metadata['chunk_id']
    try:
        graph_data = await graph_extraction_chain.ainvoke({"chunk_text": chunk.page_content})
        
        entities = []
        # Add entities to a temporary list
        for entity in graph_data.get('entities', []):
            name = entity['name'].strip().upper()
            if name:
                entities.append((name, entity.get('type', 'Unknown')))

        relationships = []
        # Add relationships to a temporary list
        for rel in graph_data.get('relationships', []):
            source = rel['source'].strip().upper()
            target = rel['target'].strip().upper()
            if source and target:
                relationships.append((source, target, rel.get('label', '')))
        
        return chunk_id, entities, relationships
            
    except Exception as e:
        logging.error(f"Failed to process chunk {chunk_id} for graph extraction: {e}")
        return chunk_id, [], []

# --- Main Processing Function ---
async def process_documents(course_id: str, force_rebuild: bool = False):
    """处理文档并构建知识图谱"""
    course_doc_dir = os.path.join("backend/uploads/materials", course_id)
    if not os.path.exists(course_doc_dir):
        logging.warning(f"Directory not found for course '{course_id}', skipping.")
        return

    persist_dir = get_or_create_course_db_path(course_id)
    metadata_file = os.path.join(persist_dir, 'processed_files_metadata.json')
    graph_file_path = os.path.join(persist_dir, 'knowledge_graph.gml')
    
    # 加载已处理文件的元数据
    processed_files_metadata = load_processed_files_metadata(metadata_file)

    if force_rebuild and os.path.exists(graph_file_path):
        logging.info("Force rebuild enabled: Removing old knowledge graph.")
        os.remove(graph_file_path)

    if force_rebuild:
        logging.info("Force rebuild enabled: Clearing old metadata to re-process all files.")
        processed_files_metadata = {}

    # 检查需要处理的文件
    files_to_process = []
    for filename in os.listdir(course_doc_dir):
        file_path = os.path.join(course_doc_dir, filename)
        if not os.path.isfile(file_path):
            continue
        
        current_hash = get_file_hash(file_path)
        if filename not in processed_files_metadata or processed_files_metadata[filename] != current_hash:
            files_to_process.append((filename, file_path))
            processed_files_metadata[filename] = current_hash

    if not files_to_process:
        logging.info("No new or modified documents to process.")
        return

    logging.info(f"Found {len(files_to_process)} new or modified files to process.")
    
    # 处理文档并构建知识图谱
    all_docs = []
    for filename, file_path in tqdm(files_to_process, desc="Loading documents"):
        try:
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".pdf":
                loader = PyMuPDFLoader(file_path)
            elif ext == ".docx":
                loader = Docx2txtLoader(file_path)
            elif ext == ".doc":
                # Convert .doc → .pdf
                try:
                    soffice = os.getenv("UNSTRUCTURED_SOFFICE_PATH", "soffice")
                    abs_in = os.path.abspath(file_path)
                    src_dir = os.path.dirname(abs_in)
                    converted_pdf = os.path.splitext(abs_in)[0] + ".pdf"
                    
                    if not os.path.exists(converted_pdf):
                        cmd = [
                            soffice,
                            "--headless",
                            "--convert-to",
                            "pdf:writer_pdf_Export",
                            abs_in,
                            "--outdir",
                            src_dir,
                        ]
                        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.returncode != 0:
                            logging.error("LibreOffice conversion failed")
                            raise RuntimeError("LibreOffice conversion failed")

                    loader = PyMuPDFLoader(converted_pdf)
                except Exception as convert_err:
                    logging.error(f"LibreOffice PDF conversion failed for {file_path}: {convert_err}")
                    loader = UnstructuredFileLoader(file_path, mode="single")
            elif ext in ['.md', '.markdown']:
                # 直接用open读取Markdown文本，避免复杂Loader
                try:
                    from langchain_core.documents import Document
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    docs = [Document(page_content=content, metadata={"source": filename})]
                    print("用open直接读取md文件成功")
                except Exception as e:
                    print(f"open读取md失败: {e}")
                    raise
            else:
                # Fallback to generic loader
                loader = UnstructuredFileLoader(file_path, mode="single")

            docs = loader.load()
            for doc in docs:
                doc.metadata['source'] = filename
            all_docs.extend(docs)
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {e}")
            if filename in processed_files_metadata:
                del processed_files_metadata[filename]
    
    if not all_docs:
        logging.info("No content loaded from new/modified files.")
        return

    # 分割文档
    logging.info(f"Splitting documents into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    splits = text_splitter.split_documents(all_docs)
    
    # 添加唯一ID
    for i, doc in enumerate(splits):
        doc.metadata['chunk_id'] = f"chunk_{i}"

    # 创建向量存储
    logging.info("Creating/updating vectorstore...")
    embedding_function = EmbeddingFunction()
    Chroma.from_documents(
        documents=splits,
        embedding=embedding_function,
        persist_directory=persist_dir
    )
    
    # 构建知识图谱
    logging.info("开始构建知识图谱...")
    try:
        def progress_callback(progress):
            logging.info(f"知识图谱构建进度: {progress:.1f}%")
        
        graph_success = build_knowledge_graph(course_id, splits, progress_callback)
        if graph_success:
            logging.info("知识图谱构建成功")
        else:
            logging.warning("知识图谱构建失败，但向量存储已创建")
    except Exception as e:
        logging.error(f"构建知识图谱时出错: {e}")
        logging.info("继续处理，向量存储已创建")
    
    # 保存元数据
    logging.info("Saving updated file metadata...")
    save_processed_files_metadata(metadata_file, processed_files_metadata)
    logging.info("Database creation/update process complete.")

FFMPEG_BIN = os.getenv("FFMPEG_PATH", "ffmpeg")  # allow override if ffmpeg not in PATH

def _locate_ffmpeg() -> str:
    """Return path to ffmpeg executable or raise a descriptive error."""
    # 1) explicit env var path
    if os.path.isfile(FFMPEG_BIN):
        logging.debug(f"Using ffmpeg from env var: {FFMPEG_BIN}")
        return FFMPEG_BIN

    # 2) PATH search
    path = _shutil.which(FFMPEG_BIN)
    if path:
        logging.debug(f"Found ffmpeg in PATH at: {path}")
        return path

    # 3) Heuristic search under common Program Files directories (Windows only)
    if os.name == 'nt':
        import glob
        candidates = []
        for base in [
            os.environ.get("ProgramFiles", r"C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")
        ]:
            pattern = os.path.join(base, "**", "ffmpeg.exe")
            candidates.extend(glob.glob(pattern, recursive=True))
        if candidates:
            logging.debug(f"Auto-detected ffmpeg candidates: {candidates[:3]}")
            return candidates[0]

    raise FileNotFoundError(
        "ffmpeg executable not found. Install FFmpeg and ensure it is in your PATH, or set "
        "environment variable FFMPEG_PATH to its full path (e.g. C:/ffmpeg/bin/ffmpeg.exe)."
    )

def extract_audio(video_path: str) -> str:
    """Extract mono 16k WAV from an mp4 file. Returns path to the wav inside a temp dir."""
    tmp_dir = tempfile.mkdtemp()
    wav_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.wav")
    ffmpeg = _locate_ffmpeg()
    cmd = [
        ffmpeg,
        "-i",
        video_path,
        "-vn",  # no video
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        wav_path,
        "-y",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav_path

def transcribe_audio(audio_path: str) -> str:
    """Send WAV to SiliconFlow transcription endpoint and return plain text."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY not set for audio transcription")

    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    model_name = "FunAudioLLM/SenseVoiceSmall"  # SiliconFlow fixed model for STT

    with open(audio_path, "rb") as f:
        files = {
            "file": (os.path.basename(audio_path), f, "audio/wav"),
            "model": (None, model_name),
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.post(url, files=files, headers=headers, timeout=120)
        resp.raise_for_status()
        # Endpoint returns text directly or JSON; assume JSON {"text": "..."}
        data = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else resp.text
        if isinstance(data, dict):
            return data.get("text", "")
        return data

def process_document_with_progress(course_id: str, file_path: str, progress_callback: Optional[Callable[[float], None]] = None):
    """Process a single document and report progress using Silicon Flow embedding model"""
    
    def report_progress(stage: str, current: int, total: int):
        """Report progress for a specific stage"""
        if progress_callback:
            # Define stage weights for overall progress calculation
            stage_weights = {
                'loading': 0.2,
                'splitting': 0.1,
                'vectorizing': 0.5,
                'graph_extraction': 0.15,
                'saving': 0.05
            }
            
            # Calculate overall progress
            stage_start = sum([w for s, w in stage_weights.items() if s < stage]) * 100
            stage_progress = (current / total) * stage_weights[stage] * 100
            total_progress = stage_start + stage_progress
            
            # Create stage message
            stage_messages = {
                'loading': '正在加载文档',
                'splitting': '正在分割文档',
                'vectorizing': '正在向量化文档',
                'graph_extraction': '正在构建知识图谱',
                'saving': '正在保存元数据'
            }
            message = stage_messages.get(stage, f'处理阶段: {stage}')
            
            # Call progress callback with stage and message
            if hasattr(progress_callback, '__code__') and progress_callback.__code__.co_argcount >= 3:
                # Progress callback supports stage and message parameters
                progress_callback(min(total_progress, 99.9), stage, message)
            else:
                # Progress callback only supports progress parameter
                progress_callback(min(total_progress, 99.9))
    
    try:
        # 设置embedding维度（siliconflow BAAI/bge-large-zh-v1.5 = 1024维）
        embedding_dimension = 1024
        
        # Set up knowledge base directory
        kb_dir = os.path.join("backend/uploads/knowledge_base", course_id)
        os.makedirs(kb_dir, exist_ok=True)
        
        # Stage 1: Loading document
        report_progress('loading', 0, 1)
        
        # Determine file type and load document
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        if ext == '.pdf':
            loader = PyMuPDFLoader(file_path)
        elif ext in ['.docx', '.doc']:
            loader = Docx2txtLoader(file_path)
        elif ext in ['.md', '.markdown']:
            # 直接用open读取Markdown文本，避免复杂Loader
            try:
                from langchain_core.documents import Document
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                docs = [Document(page_content=content, metadata={"source": filename})]
                print("用open直接读取md文件成功")
            except Exception as e:
                print(f"open读取md失败: {e}")
                raise
        else:
            # Fallback to generic loader
            loader = UnstructuredFileLoader(file_path, mode="single")
        
        if ext not in ['.md', '.markdown']:
            docs = loader.load()
        for doc in docs:
            doc.metadata['source'] = filename
        
        report_progress('loading', 1, 1)
        
        # Stage 2: Splitting document
        report_progress('splitting', 0, 1)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        splits = text_splitter.split_documents(docs)
        
        # Add a unique ID to each split
        for i, doc in enumerate(splits):
            doc.metadata['chunk_id'] = f"chunk_{i}"
        
        report_progress('splitting', 1, 1)
        
        # Stage 3: Vectorizing with Silicon Flow
        report_progress('vectorizing', 0, 1)
        
        # 创建向量数据库，使用正确的维度
        persist_dir = os.path.join(kb_dir, "vectordb")
        os.makedirs(persist_dir, exist_ok=True)
        
        # 使用现有的EmbeddingFunction类，但确保维度正确
        embedding_function = EmbeddingFunction()
        
        # 创建Chroma向量数据库，关闭遥测
        from chromadb.config import Settings
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_function,
            client_settings=Settings(anonymized_telemetry=False)
        )
        
        # Add documents to vectorstore
        print(f"准备添加文档到向量数据库，分块数量: {len(splits)}")
        for i, doc in enumerate(splits):
            print(f"chunk {i} metadata: {doc.metadata}")
            print(f"chunk {i} content: {doc.page_content[:100].replace(chr(10), ' ')} ...")
        try:
            vectorstore.add_documents(splits)
            print("add_documents 成功")
        except Exception as e:
            print("add_documents 失败:", e)
            import traceback
            traceback.print_exc()
            raise
        
        print("=== 向量化完成，准备进入知识图谱构建阶段 ===")
        report_progress('vectorizing', 100, 100)
        
        # Stage 4: Building knowledge graph
        print("=== 开始构建知识图谱 ===")
        report_progress('graph_extraction', 0, 1)
        try:
            def graph_progress_callback(progress):
                report_progress('graph_extraction', int(progress), 100)
            
            print(f"调用 build_knowledge_graph，课程ID: {course_id}，文档块数量: {len(splits)}")
            graph_success = build_knowledge_graph(course_id, splits, graph_progress_callback)
            if graph_success:
                print("✓ 知识图谱构建成功")
                logging.info("知识图谱构建成功")
            else:
                print("✗ 知识图谱构建失败，但向量存储已创建")
                logging.warning("知识图谱构建失败，但向量存储已创建")
        except Exception as e:
            print(f"✗ 构建知识图谱时出错: {e}")
            import traceback
            traceback.print_exc()
            logging.error(f"构建知识图谱时出错: {e}")
            logging.info("继续处理，向量存储已创建")
        
        print("=== 知识图谱构建阶段完成 ===")
        report_progress('graph_extraction', 1, 1)
        
        # Stage 5: Saving metadata
        report_progress('saving', 0, 1)
        
        # Save metadata about processed files
        metadata_path = os.path.join(kb_dir, 'processed_files.json')
        processed_files = {}
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                processed_files = json.load(f)
        
        # Add this file to processed files
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        processed_files[filename] = {
            'hash': file_hash,
            'processed_at': int(time.time())
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(processed_files, f, indent=2)
        
        report_progress('saving', 1, 1)
        
        return True
        
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        print(traceback.format_exc())
        if progress_callback:
            progress_callback(-1)  # Indicate error
        raise

def remove_document_from_knowledge_base(course_id: str, file_path: str) -> bool:
    """
    从知识库中删除指定文档
    
    Args:
        course_id: 课程ID
        file_path: 文件路径
        
    Returns:
        bool: 删除是否成功
    """
    try:
        # 获取知识库路径
        persist_dir = get_or_create_course_db_path(course_id)
        
        # 计算文件哈希值
        file_hash = get_file_hash(file_path)
        
        # 初始化向量数据库
        embedding_function = EmbeddingFunction()
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_function
        )
        
        # 获取所有文档
        all_docs = vectorstore.get()
        
        # 找到要删除的文档
        documents_to_remove = []
        metadatas_to_remove = []
        ids_to_remove = []
        
        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata.get('file_path') == file_path:
                documents_to_remove.append(all_docs['documents'][i])
                metadatas_to_remove.append(metadata)
                ids_to_remove.append(all_docs['ids'][i])
        
        if not ids_to_remove:
            print(f"未找到文件 {file_path} 在知识库中的记录")
            return True  # 认为删除成功，因为文件本来就不存在
        
        # 从向量数据库中删除
        vectorstore.delete(ids=ids_to_remove)
        
        # 更新元数据文件
        metadata_file = os.path.join(persist_dir, 'processed_files_metadata.json')
        processed_files = load_processed_files_metadata(metadata_file)
        
        # 删除文件记录
        if file_hash in processed_files:
            del processed_files[file_hash]
            save_processed_files_metadata(metadata_file, processed_files)
        
        # 重新构建知识图谱（删除相关节点）
        try:
            graph_path = os.path.join(persist_dir, 'knowledge_graph.gml')
            if os.path.exists(graph_path):
                G = nx.read_gml(graph_path)
                
                # 找到与删除文件相关的节点
                nodes_to_remove = []
                for node in G.nodes():
                    node_data = G.nodes[node]
                    source_chunks = node_data.get('source_chunks', [])
                    # 检查是否有chunk来自被删除的文件
                    for chunk_id in source_chunks:
                        if any(chunk_id == doc_id for doc_id in ids_to_remove):
                            nodes_to_remove.append(node)
                            break
                
                # 删除相关节点
                G.remove_nodes_from(nodes_to_remove)
                
                # 保存更新后的图谱
                nx.write_gml(G, graph_path)
                print(f"从知识图谱中删除了 {len(nodes_to_remove)} 个节点")
        except Exception as e:
            print(f"更新知识图谱时出错: {e}")
        
        print(f"成功从知识库中删除文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"删除文档时出错: {e}")
        return False

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="Create or update a course-specific vector database.")
    parser.add_argument("--course_id", help="The ID of the course to process.", required=True)
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of the database for the specified course.")
    args = parser.parse_args()
    
    asyncio.run(process_documents(args.course_id, args.rebuild))

if __name__ == "__main__":
    main()
            