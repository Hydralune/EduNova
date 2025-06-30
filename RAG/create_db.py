import os
import sys
import argparse
import hashlib
import json
import networkx as nx
from tqdm.asyncio import tqdm
from typing import List
import logging
import asyncio
import subprocess
import tempfile
import shutil
import uuid
import requests
import shutil as _shutil

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
from embedding_util import get_embedding

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurable parameters via environment variables ---
# Larger chunk reduces number of LLM calls (speed ↑) but increases prompt size.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "350"))  # 降低分块大小，适配512 tokens限制
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
# Max parallel API calls (respect provider's rate-limit)
CONCURRENCY_LIMIT = int(os.getenv("LLM_CONCURRENCY", "8"))

# --- LLM and Parser Initialization ---
def get_llm():
    """Initializes and returns the LLM."""
    # Fetch credentials from generic environment variables so that any provider compatible with
    # the OpenAI API can be plugged in by simply editing the .env file (no code changes needed).
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL")

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
    """Custom embedding function using API with a progress bar."""
    def __init__(self, batch_size=1):
        # Use batch size 1 to avoid payload too large issues
        self.batch_size = batch_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using Silicon Flow API with correct dimension"""
        try:
            from backend.rag.embedding_util import get_embedding
            
            # 分批处理
            batch_size = self.batch_size
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                result = get_embedding(batch)
                
                if 'data' in result:
                    batch_embeddings = [item['embedding'] for item in result['data']]
                    all_embeddings.extend(batch_embeddings)
                else:
                    raise Exception("Embedding API返回格式错误")
            
            # 验证维度（siliconflow BAAI/bge-large-zh-v1.5 = 1024维）
            embedding_dimension = 1024
            if all_embeddings and len(all_embeddings[0]) != embedding_dimension:
                raise Exception(f"Embedding维度不匹配: 期望{embedding_dimension}，实际{len(all_embeddings[0])}")
            
            return all_embeddings
            
        except Exception as e:
            print(f"Embedding失败: {e}")
            # 返回占位符embedding
            embedding_dimension = 1024
            return [[0.0] * embedding_dimension] * len(texts)

    def embed_query(self, text: str) -> List[float]:
        result = get_embedding(text)
        return result["data"][0]["embedding"]

# --- Helper Functions ---
def get_or_create_course_db_path(course_id: str, base_persist_dir: str = None) -> str:
    # 统一知识库路径为 backend/uploads/knowledge_base
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    KNOWLEDGE_BASE_ROOT = os.path.join(project_root, "backend", "uploads", "knowledge_base")
    persist_dir = os.path.join(KNOWLEDGE_BASE_ROOT, course_id)
    os.makedirs(persist_dir, exist_ok=True)
    return persist_dir

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_processed_files_metadata(metadata_file: str) -> dict:
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_processed_files_metadata(metadata_file: str, data: dict):
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=4)

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
    persist_dir = get_or_create_course_db_path(course_id)
    metadata_file = os.path.join(persist_dir, 'metadata.json')
    graph_file_path = os.path.join(persist_dir, 'knowledge_graph.gml')
    processed_files_metadata = load_processed_files_metadata(metadata_file)

    if force_rebuild and os.path.exists(graph_file_path):
        logging.info("Force rebuild enabled: Removing old knowledge graph.")
        os.remove(graph_file_path)

    if force_rebuild:
        logging.info("Force rebuild enabled: Clearing old metadata to re-process all files.")
        processed_files_metadata = {}

    files_to_process = []
    for filename in os.listdir(os.path.join("./documents", course_id)):
        file_path = os.path.join("./documents", course_id, filename)
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
    all_docs = []
    for filename, file_path in tqdm(files_to_process, desc="Loading documents"):
        try:
            # Determine file type and load document
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            if ext == '.pdf':
                loader = PyMuPDFLoader(file_path)
            elif ext in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
            elif ext in ['.md', '.markdown']:
                # 专门处理Markdown文件
                try:
                    from langchain_community.document_loaders import UnstructuredMarkdownLoader
                    loader = UnstructuredMarkdownLoader(file_path)
                except ImportError:
                    # 如果专门的Markdown加载器不可用，使用通用加载器
                    loader = UnstructuredFileLoader(file_path, mode="single")
            elif ext == ".mp4":
                try:
                    wav_path = extract_audio(file_path)
                    transcript = transcribe_audio(wav_path)
                    loader = None  # We'll create Document manually
                    docs = [Document(page_content=transcript, metadata={"source": filename})]
                    all_docs.extend(docs)
                    # Cleanup temp dir containing wav
                    shutil.rmtree(os.path.dirname(wav_path), ignore_errors=True)
                    continue  # Skip default loading path
                except Exception as e:
                    logging.error(f"Failed to process video {file_path}: {e}")
                    continue
            else:
                # Fallback to generic loader
                loader = UnstructuredFileLoader(file_path, mode="single")

            docs = loader.load()
            for doc in docs:
                doc.metadata['source'] = filename
            all_docs.extend(docs)
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {e}")
            # Remove the entry so that it will be retried next run after the issue is fixed
            if filename in processed_files_metadata:
                del processed_files_metadata[filename]
    
    if not all_docs:
        logging.info("No content loaded from new/modified files.")
        return

    logging.info(f"Splitting documents into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    splits = text_splitter.split_documents(all_docs)
    
    # Add a unique ID to each split
    for i, doc in enumerate(splits):
        doc.metadata['chunk_id'] = f"chunk_{i}"

    logging.info("Creating/updating vectorstore...")
    embedding_function = EmbeddingFunction()
    Chroma.from_documents(
        documents=splits,
        embedding=embedding_function,
        persist_directory=persist_dir
    )
    
    logging.info("Initializing LLM for graph extraction...")
    llm = get_llm()
    graph_extraction_chain = get_graph_extraction_chain(llm)
    
    logging.info("Building knowledge graph concurrently...")
    
    # Create a semaphore to limit concurrency (configurable)
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    logging.info(f"LLM concurrency limit set to {CONCURRENCY_LIMIT}")

    async def process_with_semaphore(chunk, chain):
        async with semaphore:
            return await process_chunk_for_graph(chunk, chain)

    # Create concurrent tasks for graph extraction
    tasks = [process_with_semaphore(chunk, graph_extraction_chain) for chunk in splits]
    results = await tqdm.gather(*tasks, desc="Extracting entities and building graph")

    # Process results synchronously to build the graph
    G = nx.Graph()
    all_extracted_entities = set()

    for chunk_id, entities, relationships in results:
        for name, ent_type in entities:
            all_extracted_entities.add(name)
            if not G.has_node(name):
                G.add_node(name, type=ent_type, source_chunks=[])
            G.nodes[name]['source_chunks'].append(chunk_id)

        for source, target, label in relationships:
            # Ensure relationship entities were also extracted to maintain consistency
            if source in all_extracted_entities and target in all_extracted_entities:
                G.add_edge(source, target, label=label)

    logging.info(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    nx.write_gml(G, graph_file_path)
    logging.info(f"Knowledge graph saved to {graph_file_path}")

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

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="Create or update a course-specific vector database.")
    parser.add_argument("--course_id", help="The ID of the course to process.", required=True)
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of the database for the specified course.")
    args = parser.parse_args()
    
    asyncio.run(process_documents(args.course_id, args.rebuild))

if __name__ == "__main__":
    main()
            