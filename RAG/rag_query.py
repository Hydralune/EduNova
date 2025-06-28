import os
import argparse
from dotenv import load_dotenv
import networkx as nx
from typing import List
import random
import time
import openai

from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from create_db import EmbeddingFunction

# Load environment variables
load_dotenv()

def format_docs(docs: List[Document]) -> str:
    """Helper function to format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_query_entities_chain(llm):
    """Creates a chain for extracting entities from the user's query."""
    prompt = ChatPromptTemplate.from_template("""
Extract the names of key concepts or entities from the following question.
Return them as a JSON list of strings.

Question:
---
{question}
---
    """)
    return prompt | llm | JsonOutputParser()

def get_graph_context(question: str, graph: nx.Graph, all_chunks: dict, llm) -> List[Document]:
    """
    Retrieves context from the knowledge graph by finding paths between entities in the query.
    """
    print("--- Identifying entities in query for graph search ---")
    query_entities_chain = get_query_entities_chain(llm)
    try:
        entities = query_entities_chain.invoke({"question": question})
        # Filter out any non-string or empty string results from the parser
        entities = [e.strip().upper() for e in entities if isinstance(e, str) and e.strip()]
        print(f"--- Found entities: {entities} ---")
    except Exception:
        print("--- Could not extract entities from query, skipping graph search. ---")
        return []

    if not entities:
        return []

    related_chunk_ids = set()
    path_docs = []

    # First, gather chunks directly related to each entity
    for entity_name in entities:
        if entity_name in graph:
            related_chunk_ids.update(graph.nodes[entity_name].get('source_chunks', []))

    # If multiple entities are found, find paths between them
    if len(entities) > 1:
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                source = entities[i]
                target = entities[j]
                if source in graph and target in graph:
                    try:
                        paths = list(nx.all_shortest_paths(graph, source=source, target=target))
                        print(f"--- Found {len(paths)} shortest path(s) between {source} and {target} ---")
                        for path in paths:
                            path_str = " -> ".join(path)
                            path_doc = Document(
                                page_content=f"Found a reasoning path: {path_str}",
                                metadata={"source": "knowledge_graph_path"}
                            )
                            path_docs.append(path_doc)
                            # Add chunks from all nodes in the path
                            for node_name in path:
                                related_chunk_ids.update(graph.nodes[node_name].get('source_chunks', []))
                    except nx.NetworkXNoPath:
                        print(f"--- No path found between {source} and {target} ---")
                        pass

    # Retrieve the unique documents from the collected chunk IDs
    graph_docs = [all_chunks[chunk_id] for chunk_id in related_chunk_ids if chunk_id in all_chunks]
    
    # Combine path descriptions with the text chunks
    final_graph_docs = path_docs + graph_docs
    print(f"--- Retrieved {len(final_graph_docs)} total documents (including paths) from the knowledge graph ---")
    return final_graph_docs

# New function to initialize resources for external use
def initialize_resources(course_id):
    """Initialize and return resources for a specific course."""
    # --- Load API Keys ---
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL")

    if not api_key:
        raise ValueError("LLM_API_KEY not found in .env file.")
    if not base_url:
        raise ValueError("LLM_API_BASE not found in .env file.")
    if not model_name:
        raise ValueError("LLM_MODEL not found in .env file.")

    # --- Initialize LLM ---
    llm = ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=base_url,
        model_name=model_name,
        temperature=0,
        max_retries=6
    )

    # --- Load Vectorstore, All Chunks, and Knowledge Graph ---
    persist_dir = os.path.join("./data", course_id)
    graph_path = os.path.join(persist_dir, 'knowledge_graph.gml')

    if not os.path.exists(persist_dir):
        raise FileNotFoundError(f"No database found for course '{course_id}'. Please run create_db.py first.")
        
    if not os.path.exists(graph_path):
        print(f"Warning: No knowledge graph found for course '{course_id}'. Proceeding with vector search only.")
        G = nx.Graph()  # Empty graph
    else:
        G = nx.read_gml(graph_path)
    
    embedding_function = EmbeddingFunction()
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_function
    )
    
    # Load all documents from the vectorstore to cross-reference with the graph
    all_docs_from_db = vectorstore.get()
    all_chunks_map = {doc['chunk_id']: Document(page_content=content, metadata=doc) 
                     for content, doc in zip(all_docs_from_db['documents'], all_docs_from_db['metadatas'])}

    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    return {
        'llm': llm,
        'graph': G,
        'all_chunks_map': all_chunks_map,
        'vector_retriever': vector_retriever
    }

# Expose hybrid_retriever for external use
def hybrid_retriever(query: str, course_id: str):
    """Retrieves relevant documents using hybrid search (graph + vector) for a given query and course."""
    resources = initialize_resources(course_id)
    
    # Get context from the graph
    graph_docs = get_graph_context(query, resources['graph'], resources['all_chunks_map'], resources['llm'])
    
    # Get context from vector search
    print("--- Performing vector search ---")
    vector_docs = resources['vector_retriever'].invoke(query)
    print(f"--- Retrieved {len(vector_docs)} chunks from vector search ---")

    # Combine and de-duplicate
    combined_docs_map = {doc.metadata['chunk_id']: doc for doc in graph_docs + vector_docs 
                        if 'chunk_id' in doc.metadata}
    
    # Add path documents, which don't have chunk_ids
    path_docs = [doc for doc in graph_docs if doc.metadata.get('source') == 'knowledge_graph_path']
    
    final_docs = path_docs + list(combined_docs_map.values())
    print(f"--- Total unique documents for context: {len(final_docs)} ---")
    return final_docs

def main():
    parser = argparse.ArgumentParser(description="Query a course-specific vector database.")
    parser.add_argument("--course_id", type=str, required=True, help="ID of the course to query.")
    args = parser.parse_args()

    # --- Initialize Resources ---
    try:
        resources = initialize_resources(args.course_id)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {str(e)}")
        return

    # --- Display Sample Entities ---
    G = resources['graph']
    if G.number_of_nodes() > 0:
        print("\n--- Sample of Extracted Entities ---")
        sample_nodes = random.sample(list(G.nodes()), min(10, G.number_of_nodes()))
        for node in sample_nodes:
            print(f"- {node} (Type: {G.nodes[node].get('type', 'N/A')})")
    else:
        print("\n--- Knowledge graph is empty or could not be loaded. ---")

    # --- Define RAG Chain ---
    template = """You are a helpful and knowledgeable AI assistant.
Use the following retrieved context as your primary source to answer the user's question.
If the context is incomplete or lacks sufficient detail, supplement it with your own general knowledge to provide a thorough and accurate answer.
If the context includes code snippets, display them clearly in a code block.
When you provide actual (non-pseudocode) code, ensure it is complete and runnable. If the context does not include enough information, fill in the missing parts using your own knowledge.
When appropriate, combine the context and your own expertise to generate extended outputs, such as lesson plans, assignments, examples, or detailed explanations.
Always aim for clarity, correctness, and relevance.
If you genuinely do not know the answer, say "I don't know" instead of guessing.

Question: {question}

Context: {context}

Answer:"""
    prompt = PromptTemplate.from_template(template)

    rag_chain = (
        {"context": RunnablePassthrough() | (lambda query: hybrid_retriever(query, args.course_id)) | format_docs, "question": RunnablePassthrough()}
        | prompt
        | resources['llm']
        | StrOutputParser()
    )

    # --- Conversation Loop ---
    print("\n--- Starting Conversation Loop ---")
    while True:
        try:
            query = input("\n[You]: ")
            if query.lower() in ["exit", "quit"]:
                break
            
            print("\n[AI]:")
            
            # Add a more patient retry loop for the whole chain
            for attempt in range(3): # Retry up to 3 times
                try:
                    for chunk in rag_chain.stream(query):
                        print(chunk, end="", flush=True)
                    print() # for newline after streaming
                    break # Success, exit retry loop
                except openai.RateLimitError as e:
                    wait_time = (attempt + 1) * 5 # Wait 5s, then 10s
                    print(f"\n[System]: API rate limit reached. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
            else: # If all retries fail
                print("\n[System]: Could not get a response after multiple retries due to persistent rate limiting.")


        except (KeyboardInterrupt, EOFError):
            break
    print("\n--- Exiting ---")

if __name__ == "__main__":
    main()