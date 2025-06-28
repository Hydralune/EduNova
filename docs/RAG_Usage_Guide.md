# EduNova RAG Feature: Step-by-Step Guide

This document provides a complete walkthrough for using the AI-powered chat feature in EduNova, from setting up your environment to interacting with the AI.

---

### **Step 1: Environment Setup (One-Time)**

Before running the application, you must configure your local environment.

#### **1.1. Set Environment Variables**

The backend requires API keys and other configuration details to be set in an environment file.

1.  Navigate to the `backend/` directory.
2.  If it doesn't exist, create a file named `.env`.
3.  Copy the contents below into your `.env` file.

```dotenv
# Flask and Database Configuration
FLASK_APP=run.py
FLASK_DEBUG=True
JWT_SECRET_KEY='your-super-secret-key-please-change-me'
SQLALCHEMY_DATABASE_URI='sqlite:///app.db'

# DeepSeek/SiliconFlow API Configuration
# Get these from your SiliconFlow dashboard
DEEPSEEK_API_KEY='your-deepseek-api-key'
DEEPSEEK_API_BASE='https://api.siliconflow.cn/v1'
DEEPSEEK_MODEL='deepseek-chat'
```

**IMPORTANT**: Replace `'your-deepseek-api-key'` with your actual API key from SiliconFlow. You can also change the `JWT_SECRET_KEY` to any random string.

#### **1.2. Database Initialization**

If this is your first time running the app or if you've changed the database models, you must initialize and migrate the database.

1.  Open your terminal in the `backend/` directory.
2.  Run the following commands in order:
    ```bash
    # Set the Flask app context (if not already set in your terminal)
    $env:FLASK_APP="run.py" 
    
    # Initialize the database (only run this the very first time)
    flask db init

    # Create the migration script
    flask db migrate -m "Initial migration with all models"

    # Apply the migration to the database
    flask db upgrade
    ```

---

### **Step 2: Running the Application**

1.  Open your terminal in the `backend/` directory.
2.  Run the Flask application:
    ```bash
    flask run
    ```
3.  You should see output indicating the server is running, along with messages from the `RAGService`, `LLMService`, and `RerankerService` confirming they have been initialized.
4.  In a separate terminal, navigate to the `frontend/` directory and start the Vue development server (e.g., `npm run dev`).

---

### **Step 3: Using the RAG Chat Feature**

This is a walkthrough of the user flow.

#### **3.1. Register and Log In**

-   Use the frontend application to register a new user account (this user will be a teacher).
-   Log in with the newly created account.

#### **3.2. Create a Course**

-   From the dashboard, create a new course. Give it a name and a description.

#### **3.3. Upload a Document**

1.  Navigate to the course you just created.
2.  Find the "Upload Document" feature.
3.  Select and upload a file. **You can use a `.doc`, `.docx`, `.pdf`, or `.txt` file.** For this test, you can use the `backend/uploads/3/cp09--Python.doc` file you mentioned.
4.  After the upload is complete, watch the **backend terminal logs**. You should see messages like:
    -   `Loading index for course <course_id>...`
    -   `Indexing <X> nodes from <path_to_your_document>...`
    -   `Successfully indexed document and persisted index for course <course_id>`

These logs confirm that the RAG service has successfully processed and stored your document in the course's local knowledge base.

#### **3.4. Chat with the AI**

1.  Navigate to the chat interface for the course.
2.  Ask a question that is **specifically related to the content of the document you uploaded.**
    -   *Good Question Example:* "What are the main topics covered in the Python document?"
    -   *Bad Question Example:* "What is the capital of France?" (The AI should respond that it cannot answer from the provided documents).
3.  The system will now perform the full RAG pipeline:
    -   It will retrieve relevant text chunks from your document.
    -   It will rerank them for accuracy.
    -   It will send the best chunks and your question to the DeepSeek API.
    -   The final answer will be displayed in the chat window.

You have now successfully used the end-to-end RAG feature! 