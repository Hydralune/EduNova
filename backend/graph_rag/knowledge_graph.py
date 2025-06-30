import os
import sys
import json
import networkx as nx
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import requests
from pathlib import Path
import time

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 配置参数
GRAPH_BATCH_SIZE = int(os.getenv("GRAPH_BATCH_SIZE", "5"))
GRAPH_DELAY = float(os.getenv("GRAPH_DELAY", "0.1"))
GRAPH_CONCURRENCY = int(os.getenv("GRAPH_CONCURRENCY", "8"))

class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, course_id: str, progress_callback=None):
        self.course_id = course_id
        self.progress_callback = progress_callback
        self.api_key = os.getenv("LLM_API_KEY", "sk-dfthbfklqzgxhhrfiwukmgfakpcfuletjjvapquirwwcuteh")
        self.api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        self.model_name = "Qwen/Qwen3-14B"
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            model_name=self.model_name,
            temperature=0,
            max_retries=3
        )
        
        # 设置路径
        self.kb_dir = os.path.join("backend/uploads/knowledge_base", course_id)
        self.graph_path = os.path.join(self.kb_dir, 'knowledge_graph.gml')
        self.metadata_path = os.path.join(self.kb_dir, 'graph_metadata.json')
        
        # 确保目录存在
        os.makedirs(self.kb_dir, exist_ok=True)
        
        # 初始化图
        self.graph = nx.Graph()
        
        # 创建提取链
        self.extraction_chain = self._create_extraction_chain()
        
    def _create_extraction_chain(self):
        """创建实体和关系提取链"""
        prompt = ChatPromptTemplate.from_template('''
从以下文本中提取关键实体和它们之间的关系。

文本：
---
{text}
---

请以JSON格式返回结果，包含两个字段：
1. "entities": 实体列表，每个实体包含 "name"（实体名称）和 "type"（实体类型，如概念、技术、人物等）
2. "relationships": 关系列表，每个关系包含 "source"（源实体）、"target"（目标实体）和 "label"（关系描述）

返回格式示例：
{{
  "entities": [
    {{"name": "Python", "type": "编程语言"}},
    {{"name": "机器学习", "type": "技术领域"}}
  ],
  "relationships": [
    {{"source": "Python", "target": "机器学习", "label": "用于"}}
  ]
}}

只返回JSON格式的结果，不要包含其他文字。
''')
        
        return prompt | self.llm | JsonOutputParser()
    
    async def extract_entities_and_relationships_async(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """异步从文本中提取实体和关系"""
        try:
            result = await self.extraction_chain.ainvoke({"text": text})
            entities = result.get("entities", [])
            relationships = result.get("relationships", [])
            return entities, relationships
        except Exception as e:
            logging.error(f"提取实体和关系时出错: {e}")
            return [], []
    
    async def process_chunk_batch(self, chunks: List[Document]) -> List[Tuple[str, List[Dict], List[Dict]]]:
        """批量处理文档块"""
        semaphore = asyncio.Semaphore(GRAPH_CONCURRENCY)
        
        async def process_single_chunk(chunk):
            async with semaphore:
                chunk_id = chunk.metadata.get('chunk_id', 'unknown')
                entities, relationships = await self.extract_entities_and_relationships_async(chunk.page_content)
                await asyncio.sleep(GRAPH_DELAY)  # 减少延迟
                return chunk_id, entities, relationships
        
        # 并发处理所有块
        tasks = [process_single_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"处理块时出错: {result}")
                continue
            processed_results.append(result)
        
        return processed_results
    
    async def build_graph_from_chunks_async(self, chunks: List[Document]) -> nx.Graph:
        """异步从文档块构建知识图谱"""
        logging.info(f"开始构建知识图谱，处理 {len(chunks)} 个文档块...")
        
        graph = nx.Graph()
        entity_count = 0
        relationship_count = 0
        
        # 分批处理
        for i in range(0, len(chunks), GRAPH_BATCH_SIZE):
            batch = chunks[i:i + GRAPH_BATCH_SIZE]
            logging.info(f"处理批次 {i//GRAPH_BATCH_SIZE + 1}/{(len(chunks) + GRAPH_BATCH_SIZE - 1)//GRAPH_BATCH_SIZE}")
            
            # 更新进度
            if self.progress_callback:
                progress = (i / len(chunks)) * 100
                self.progress_callback(progress)
            
            # 批量处理
            batch_results = await self.process_chunk_batch(batch)
            
            # 处理结果
            for chunk_id, entities, relationships in batch_results:
                # 添加实体到图中
                for entity in entities:
                    name = entity.get("name", "").strip().upper()
                    entity_type = entity.get("type", "Unknown")
                    
                    if name and len(name) > 1:  # 过滤掉太短的实体
                        if not graph.has_node(name):
                            graph.add_node(name, type=entity_type, source_chunks=[])
                            entity_count += 1
                        
                        # 记录来源块
                        if chunk_id not in graph.nodes[name]['source_chunks']:
                            graph.nodes[name]['source_chunks'].append(chunk_id)
                
                # 添加关系到图中
                for rel in relationships:
                    source = rel.get("source", "").strip().upper()
                    target = rel.get("target", "").strip().upper()
                    label = rel.get("label", "")
                    
                    if source and target and source != target:
                        # 确保两个实体都存在
                        if not graph.has_node(source):
                            graph.add_node(source, type="Unknown", source_chunks=[])
                            entity_count += 1
                        if not graph.has_node(target):
                            graph.add_node(target, type="Unknown", source_chunks=[])
                            entity_count += 1
                        
                        # 添加边
                        if not graph.has_edge(source, target):
                            graph.add_edge(source, target, label=label)
                            relationship_count += 1
        
        # 完成进度
        if self.progress_callback:
            self.progress_callback(100.0)
        
        logging.info(f"知识图谱构建完成: {entity_count} 个实体, {relationship_count} 个关系")
        return graph
    
    def build_graph_from_chunks(self, chunks: List[Document]) -> nx.Graph:
        """从文档块构建知识图谱（同步接口）"""
        # 运行异步函数
        return asyncio.run(self.build_graph_from_chunks_async(chunks))
    
    def save_graph(self, graph: nx.Graph):
        """保存知识图谱"""
        try:
            # 保存GML格式
            nx.write_gml(graph, self.graph_path)
            
            # 保存元数据
            metadata = {
                "course_id": self.course_id,
                "created_at": int(time.time()),
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
                "model_used": self.model_name
            }
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logging.info(f"知识图谱已保存到: {self.graph_path}")
            
        except Exception as e:
            logging.error(f"保存知识图谱时出错: {e}")
    
    def load_graph(self) -> nx.Graph:
        """加载知识图谱"""
        try:
            if os.path.exists(self.graph_path):
                graph = nx.read_gml(self.graph_path)
                logging.info(f"已加载知识图谱: {graph.number_of_nodes()} 个节点, {graph.number_of_edges()} 条边")
                return graph
            else:
                logging.warning("知识图谱文件不存在")
                return nx.Graph()
        except Exception as e:
            logging.error(f"加载知识图谱时出错: {e}")
            return nx.Graph()

class KnowledgeGraphRetriever:
    """知识图谱检索器"""
    
    def __init__(self, course_id: str):
        self.course_id = course_id
        self.api_key = os.getenv("LLM_API_KEY", "sk-dfthbfklqzgxhhrfiwukmgfakpcfuletjjvapquirwwcuteh")
        self.api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        # 检索时用.env配置模型
        self.model_name = os.getenv("LLM_MODEL", "Qwen/Qwen3-32B")
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            model_name=self.model_name,
            temperature=0.7,
            max_retries=3
        )
        
        # 设置路径
        self.kb_dir = os.path.join("backend/uploads/knowledge_base", course_id)
        self.graph_path = os.path.join(self.kb_dir, 'knowledge_graph.gml')
        
        # 加载图
        self.graph = self.load_graph()
        
    def load_graph(self) -> nx.Graph:
        """加载知识图谱"""
        try:
            if os.path.exists(self.graph_path):
                graph = nx.read_gml(self.graph_path)
                logging.info(f"已加载知识图谱: {graph.number_of_nodes()} 个节点, {graph.number_of_edges()} 条边")
                return graph
            else:
                logging.warning("知识图谱文件不存在")
                return nx.Graph()
        except Exception as e:
            logging.error(f"加载知识图谱时出错: {e}")
            return nx.Graph()
    
    def extract_query_entities(self, query: str) -> List[str]:
        """从查询中提取实体"""
        try:
            prompt = ChatPromptTemplate.from_template('''
从以下问题中提取关键实体名称。

问题：
---
{query}
---

请以JSON格式返回实体名称列表，格式如下：
{{
  "entities": ["实体1", "实体2", "实体3"]
}}

只返回JSON格式的结果，不要包含其他文字。
''')
            
            chain = prompt | self.llm | JsonOutputParser()
            result = chain.invoke({"query": query})
            
            entities = result.get("entities", [])
            # 转换为大写以匹配图中的节点
            entities = [entity.strip().upper() for entity in entities if entity.strip()]
            
            return entities
            
        except Exception as e:
            logging.error(f"提取查询实体时出错: {e}")
            return []
    
    def find_related_nodes(self, entities: List[str], max_depth: int = 2) -> List[str]:
        """查找与查询实体相关的节点"""
        related_nodes = set()
        
        for entity in entities:
            if entity in self.graph:
                # 添加实体本身
                related_nodes.add(entity)
                
                # 查找邻居节点
                neighbors = list(self.graph.neighbors(entity))
                related_nodes.update(neighbors)
                
                # 查找更深层的相关节点
                if max_depth > 1:
                    for neighbor in neighbors:
                        if neighbor in self.graph:
                            second_neighbors = list(self.graph.neighbors(neighbor))
                            related_nodes.update(second_neighbors)
        
        return list(related_nodes)
    
    def get_subgraph_context(self, nodes: List[str]) -> str:
        """获取子图的上下文信息"""
        if not nodes:
            return ""
        
        context_parts = []
        
        for node in nodes:
            if node in self.graph:
                node_data = self.graph.nodes[node]
                node_type = node_data.get('type', 'Unknown')
                
                # 获取与该节点相关的边
                edges = []
                for neighbor in self.graph.neighbors(node):
                    edge_data = self.graph.edges[node, neighbor]
                    edge_label = edge_data.get('label', '')
                    edges.append(f"{node} --{edge_label}--> {neighbor}")
                
                # 构建节点描述
                node_desc = f"实体: {node} (类型: {node_type})"
                if edges:
                    node_desc += f"\n关系: {'; '.join(edges)}"
                
                context_parts.append(node_desc)
        
        return "\n\n".join(context_parts)
    
    def query_with_graph_context_stream(self, query: str, max_depth: int = 2):
        """使用知识图谱上下文进行流式查询"""
        try:
            logging.info(f"开始知识图谱查询: {query}")
            
            # 提取查询中的实体
            entities = self.extract_query_entities(query)
            logging.info(f"提取的实体: {entities}")
            
            if not entities:
                yield "无法从查询中识别出相关实体。"
                return
            
            # 查找相关节点
            related_nodes = self.find_related_nodes(entities, max_depth)
            logging.info(f"找到 {len(related_nodes)} 个相关节点")
            
            if not related_nodes:
                yield "在知识图谱中未找到与查询相关的信息。"
                return
            
            # 获取子图上下文
            graph_context = self.get_subgraph_context(related_nodes)
            
            # 构建提示词
            prompt = f"""基于以下信息回答问题：

相关信息：
{graph_context}

问题：{query}

请基于上述信息提供准确、详细的回答。回答要自然流畅，不要提及"基于知识图谱信息"等字眼。

回答："""
            
            # 发送流式请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7,
                "stream": True
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data_json = json.loads(data_str)
                                if 'choices' in data_json and len(data_json['choices']) > 0:
                                    delta = data_json['choices'][0].get('delta', {})
                                    if 'content' in delta and delta['content'] is not None:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                logging.error(f"LLM请求失败: {response.status_code} - {response.text}")
                yield f"抱歉，处理请求时出现错误：{response.text}"
                
        except Exception as e:
            logging.error(f"知识图谱查询时出错: {e}")
            yield f"抱歉，查询过程中出现错误：{str(e)}"

def build_knowledge_graph(course_id: str, chunks: List[Document], progress_callback=None) -> bool:
    """构建知识图谱的主函数"""
    try:
        builder = KnowledgeGraphBuilder(course_id, progress_callback)
        graph = builder.build_graph_from_chunks(chunks)
        builder.save_graph(graph)
        return True
    except Exception as e:
        logging.error(f"构建知识图谱失败: {e}")
        return False

def query_knowledge_graph_stream(course_id: str, query: str):
    """查询知识图谱的主函数（流式）"""
    try:
        retriever = KnowledgeGraphRetriever(course_id)
        for chunk in retriever.query_with_graph_context_stream(query):
            yield chunk
    except Exception as e:
        logging.error(f"查询知识图谱失败: {e}")
        yield f"查询失败：{str(e)}"

def query_knowledge_graph(course_id: str, query: str) -> str:
    """查询知识图谱的主函数（非流式）"""
    try:
        retriever = KnowledgeGraphRetriever(course_id)
        response = ""
        for chunk in retriever.query_with_graph_context_stream(query):
            response += chunk
        return response
    except Exception as e:
        logging.error(f"查询知识图谱失败: {e}")
        return f"查询失败：{str(e)}" 