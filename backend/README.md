# EduNova - Backend

This directory contains the backend server for the EduNova intelligent education assistant platform. The backend is built with Flask and provides RESTful APIs for the frontend application.

## Directory Structure

```
backend/
├── api/                  # API endpoints organized by functionality
│   ├── admin.py          # Admin-related endpoints
│   ├── auth.py           # Authentication endpoints
│   ├── learning.py       # Learning-related endpoints
│   ├── rag_ai.py         # RAG AI integration endpoints
│   └── user.py           # User management endpoints
├── config/               # Configuration files
├── models/               # Database models
│   ├── assessment.py     # Assessment-related models
│   ├── course.py         # Course-related models
│   ├── learning.py       # Learning-related models
│   ├── material.py       # Learning material models
│   └── user.py           # User models
├── utils/                # Utility functions
├── uploads/              # Directory for uploaded files
│   └── materials/        # Learning materials storage
├── main.py               # Application entry point
└── run_server.py         # Server startup script
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip or conda for package management

### Environment Setup

1. Create and activate a virtual environment:

```bash
# Using conda
conda create --name edunova python=3.9
conda activate edunova

# Or using venv
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following content:

```
# Flask configuration
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# Database configuration
DATABASE_URL=sqlite:///database/app.db

# DeepSeek API (for AI features)
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Database Initialization

```bash
# Set Flask application
# Windows PowerShell
$env:FLASK_APP = "main.py"
# Windows CMD
set FLASK_APP=main.py
# macOS/Linux
export FLASK_APP=main.py

# Initialize database
python init_db.py
```

### Running the Server

```bash
python run_server.py
```

The server will start on http://127.0.0.1:5001 by default.

## API Documentation

The backend provides the following main API endpoints:

- `/api/auth/*` - Authentication endpoints (login, register, token refresh)
- `/api/user/*` - User management endpoints
- `/api/admin/*` - Admin-specific endpoints
- `/api/learning/*` - Learning-related endpoints
- `/api/rag/*` - RAG AI integration endpoints

For detailed API documentation, refer to the project's main documentation. 