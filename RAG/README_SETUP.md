# EduNova RAG Chat Integration Setup

This document provides instructions for setting up the RAG (Retrieval Augmented Generation) integration with the EduNova chat interface.

## Prerequisites

1. Make sure you have set up the environment variables as described in `RAG/README.md`:

```
# Create a .env file in the RAG directory with the following contents:
DEEPSEEK_API_KEY='your-api-key'
DEEPSEEK_API_BASE='https://api.siliconflow.cn/v1'
DEEPSEEK_MODEL='deepseek-ai/DeepSeek-V3'

# Or use LLM prefixed variables (these take precedence)
LLM_API_KEY='your-api-key'
LLM_API_BASE='https://api.siliconflow.cn/v1'
LLM_MODEL='deepseek-ai/DeepSeek-V3'
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Creating Course Knowledge Bases

Before using the RAG-enhanced chat feature, you need to create a knowledge base for each course:

1. Upload course materials through the course detail page in the web interface
2. The system will automatically process these documents and create a vector database

Alternatively, you can manually create a knowledge base for a course using the command line:

```bash
# Navigate to the RAG directory
cd RAG

# Create a knowledge base for a specific course
python create_db.py --course_id 003
```

## Integration Components

The integration between the chat interface and RAG system involves these components:

1. **Backend API** (`backend/api/rag_ai.py`): Handles chat requests and integrates with the RAG system
2. **Frontend Component** (`frontend/src/components/ai/AIAssistant.vue`): Provides the chat interface and passes course context
3. **RAG Module** (`RAG/rag_query.py`): Performs document retrieval and query processing

## Using the RAG Chat

To use the RAG-enhanced chat:

1. Log in to the EduNova platform
2. Navigate to a course detail page
3. Click on the "智能助手" (Smart Assistant) tab
4. Ask questions related to the course materials

The system will:
1. Retrieve relevant content from the course materials
2. Generate a response based on the retrieved content
3. Display the response with citations to the source materials

## Troubleshooting

If you encounter issues with the RAG integration:

1. **Chat doesn't use RAG**: Check if the course has materials uploaded and processed
2. **API errors**: Verify your API keys in the .env file
3. **Missing dependencies**: Make sure all required packages are installed
4. **Document processing fails**: Check the format of uploaded documents (PDF, DOCX, TXT are supported)

## Advanced Configuration

You can adjust the RAG behavior by modifying these parameters:

- **Number of retrieved documents**: Edit the `search_kwargs={"k": 5}` parameter in `RAG/rag_query.py`
- **Chunk size**: Set the `CHUNK_SIZE` environment variable (default is 1000 characters)
- **Model temperature**: Modify the temperature value in the API request (lower for more factual responses) 