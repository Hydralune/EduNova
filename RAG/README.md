# DeepSeek API Tools

This package provides tools for interacting with DeepSeek AI's API, including chat completions, embeddings, and RAG implementation.

## Setup

1. Create a `.env` file in the root directory with the following contents:
   ```
   DEEPSEEK_API_KEY='your-api-key'
   DEEPSEEK_API_BASE='https://api.siliconflow.cn/v1'
   DEEPSEEK_MODEL='deepseek-ai/DeepSeek-V3'
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Files and Utilities

### Basic Chat API
- `rag_query.py`: Core functions for loading API configuration and getting responses from the chat model.

### Embedding Utilities
- `embedding_util.py`: Functions for generating embeddings from text using DeepSeek's embedding API.
- `batch_embedding.py`: Batch processing utility for generating embeddings for multiple documents efficiently.

### Document Processing and Vector Database
- `database/create_db.py`: Functions for loading and processing documents, creating vector databases.
- `qa_chain/get_vectordb.py`: Utilities for managing vector database creation or loading.
- `create_knowledge_db.py`: Command-line tool to create a vector database from documents.

### RAG Implementation Examples
- `rag_example.py`: Simple RAG implementation using keyword matching.
- `enhanced_rag.py`: Advanced RAG implementation using embeddings for semantic search.

## Document Processing Features

### Supported File Types
- PDF: Uses PyMuPDFLoader
- Markdown: Uses UnstructuredMarkdownLoader (excludes files containing "不存在" or "风控")
- Text Files: Uses UnstructuredFileLoader

### Text Processing
- Automatically splits documents into chunks (500 characters with 150 character overlap)
- Creates vector embeddings using the DeepSeek API
- Stores in Chroma vector database for efficient retrieval

## Usage Examples

### Creating a Vector Database from Documents
```bash
python create_knowledge_db.py --doc_dir ./documents --db_dir ./data
```

### Basic Chat API
```python
from rag_query import get_model_response

# Get a response from the model
prompt = "Your prompt here"
response = get_model_response(prompt)
print(response)
```

### Generating Embeddings
```python
from embedding_util import get_embedding

# Get embedding for a single text
text = "Your text here"
embedding_response = get_embedding(text)
embedding_vector = embedding_response["data"][0]["embedding"]
```

### Batch Embeddings
```python
from batch_embedding import batch_embed

documents = ["Document 1", "Document 2", "Document 3", ...]
embeddings = batch_embed(documents, batch_size=10)
```

### Enhanced RAG with Embeddings
```python
from enhanced_rag import enhanced_rag_query

documents = ["Document 1", "Document 2", "Document 3", ...]
query = "Your question here"
response = enhanced_rag_query(query, documents, top_k=3)
print(response)
```

### Using the Vector Database for RAG
```python
from qa_chain.get_vectordb import get_vectordb
from rag_query import get_model_response

# Load or create vector database
vectordb = get_vectordb(doc_dir="./documents", persist_dir="./data")

# Query the database
query = "Your question here"
docs = vectordb.similarity_search(query, k=3)

# Create context from retrieved documents
context = "\n\n".join([doc.page_content for doc in docs])

# Create prompt with context
prompt = f"""Based on the following information, answer the query.

Context:
{context}

Query: {query}

Please provide a comprehensive answer based on the given context."""

# Get response from model
response = get_model_response(prompt)
print(response)
```

## Customization

You can customize the API calls with additional parameters:

```python
response = get_model_response(
    prompt="Your prompt here",
    temperature=0.5,  # Lower temperature for more focused responses
    max_tokens=1000   # Limit response length
)
``` 