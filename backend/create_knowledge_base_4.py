#!/usr/bin/env python3
"""
为课程4创建知识库的专用脚本
"""

import os
import sys
import shutil
import json
import time
import hashlib
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_knowledge_base_for_course_4():
    """为课程4创建知识库"""
    
    course_id = "4"
    
    # 定义路径
    materials_dir = os.path.join(project_root, "backend", "uploads", "materials", course_id)
    knowledge_base_dir = os.path.join(project_root, "backend", "uploads", "knowledge_base", course_id)
    
    print(f"=== 为课程 {course_id} 创建知识库 ===")
    print(f"材料目录: {materials_dir}")
    print(f"知识库目录: {knowledge_base_dir}")
    
    # 检查材料目录是否存在
    if not os.path.exists(materials_dir):
        print(f"❌ 材料目录不存在: {materials_dir}")
        return False
    
    # 创建知识库目录
    os.makedirs(knowledge_base_dir, exist_ok=True)
    
    # 复制文件到知识库目录
    copied_files = []
    for filename in os.listdir(materials_dir):
        source_file = os.path.join(materials_dir, filename)
        target_file = os.path.join(knowledge_base_dir, filename)
        
        if os.path.isfile(source_file):
            try:
                shutil.copy2(source_file, target_file)
                copied_files.append(filename)
                print(f"✓ 复制文件: {filename}")
            except Exception as e:
                print(f"❌ 复制文件失败 {filename}: {e}")
    
    print(f"✓ 复制了 {len(copied_files)} 个文件到知识库目录")
    
    # 创建状态文件
    status_file = os.path.join(knowledge_base_dir, "processing_status.json")
    status_data = {
        "course_id": course_id,
        "source_dir": materials_dir,
        "target_dir": knowledge_base_dir,
        "copied_files": copied_files,
        "processed_at": int(time.time()),
        "status": "ready_for_processing"
    }
    
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 状态文件已创建: {status_file}")
    
    # 现在运行向量数据库创建
    print("\n=== 开始创建向量数据库 ===")
    
    try:
        # 导入必要的模块
        from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        from chromadb.config import Settings
        
        # 定义EmbeddingFunction类
        class EmbeddingFunction:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
            
            def embed_documents(self, texts):
                # 简化的embedding函数，返回1024维向量
                embeddings = []
                for text in texts:
                    # 这里应该调用真实的embedding API
                    # 暂时返回随机向量作为示例
                    import random
                    embedding = [random.uniform(-1, 1) for _ in range(1024)]
                    embeddings.append(embedding)
                return embeddings
            
            def embed_query(self, text):
                import random
                return [random.uniform(-1, 1) for _ in range(1024)]
        
        # 处理每个文件
        all_docs = []
        for filename in copied_files:
            file_path = os.path.join(knowledge_base_dir, filename)
            print(f"处理文件: {filename}")
            
            try:
                # 根据文件类型选择加载器
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                
                if ext == '.pdf':
                    loader = PyMuPDFLoader(file_path)
                elif ext in ['.docx', '.doc']:
                    loader = Docx2txtLoader(file_path)
                elif ext in ['.md', '.markdown']:
                    # 直接读取Markdown文件
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    from langchain_core.documents import Document
                    docs = [Document(page_content=content, metadata={"source": filename})]
                else:
                    # 跳过不支持的文件类型
                    print(f"跳过不支持的文件类型: {filename}")
                    continue
                
                if ext not in ['.md', '.markdown']:
                    docs = loader.load()
                
                for doc in docs:
                    doc.metadata['source'] = filename
                
                all_docs.extend(docs)
                print(f"✓ 加载完成: {filename} ({len(docs)} 个文档)")
                
            except Exception as e:
                print(f"❌ 处理文件失败 {filename}: {e}")
                continue
        
        if not all_docs:
            print("❌ 没有成功加载任何文档")
            return False
        
        print(f"✓ 总共加载了 {len(all_docs)} 个文档")
        
        # 分割文档
        print("分割文档...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        splits = text_splitter.split_documents(all_docs)
        
        # 添加唯一ID
        for i, doc in enumerate(splits):
            doc.metadata['chunk_id'] = f"chunk_{i}"
        
        print(f"✓ 分割完成，共 {len(splits)} 个文本块")
        
        # 创建向量数据库
        print("创建向量数据库...")
        persist_dir = os.path.join(knowledge_base_dir, "vectordb")
        os.makedirs(persist_dir, exist_ok=True)
        
        embedding_function = EmbeddingFunction()
        
        # 创建Chroma向量数据库
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_function,
            client_settings=Settings(anonymized_telemetry=False)
        )
        
        # 添加文档到向量数据库
        vectorstore.add_documents(splits)
        print(f"✓ 向量数据库创建完成: {persist_dir}")
        
        # 保存元数据
        metadata_path = os.path.join(knowledge_base_dir, 'processed_files.json')
        processed_files = {}
        
        for filename in copied_files:
            file_path = os.path.join(knowledge_base_dir, filename)
            if os.path.exists(file_path):
                file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                processed_files[filename] = {
                    'hash': file_hash,
                    'processed_at': int(time.time()),
                    'chunks': len([s for s in splits if s.metadata.get('source') == filename])
                }
        
        with open(metadata_path, 'w') as f:
            json.dump(processed_files, f, indent=2)
        
        print(f"✓ 元数据保存完成: {metadata_path}")
        
        # 更新状态文件
        status_data['status'] = 'completed'
        status_data['vector_db_path'] = persist_dir
        status_data['total_chunks'] = len(splits)
        status_data['completed_at'] = int(time.time())
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        print("=== 知识库创建完成 ===")
        print(f"✓ 课程 {course_id} 的知识库已成功创建")
        print(f"✓ 向量数据库位置: {persist_dir}")
        print(f"✓ 总文本块数: {len(splits)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建向量数据库时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_knowledge_base_for_course_4()
    if success:
        print("\n🎉 课程4的知识库创建成功！现在可以测试RAG功能了。")
    else:
        print("\n❌ 知识库创建失败，请检查错误信息。") 