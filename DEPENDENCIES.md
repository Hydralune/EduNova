# EduNova Dependencies

This document explains the dependency structure of the EduNova project and how to install all required dependencies.

## Project Structure

The project is organized as follows:

- `requirements.txt`: Contains all Python dependencies for the backend and RAG modules
- `package.json`: Root package.json with project metadata and scripts
- `frontend/package.json`: Frontend-specific dependencies

## Installing Backend Dependencies

To install all backend dependencies, run:

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Installing Frontend Dependencies

To install all frontend dependencies, run:

```bash
# Install dependencies
npm install

# Or, to install only frontend dependencies
cd frontend
npm install
```

## Running the Application

From the project root:

```bash
# Start the backend
npm run start:backend
# Or: cd backend && python run.py

# Start the frontend (in a separate terminal)
npm run start:frontend
# Or: cd frontend && npm run dev
```

## Notes on Dependency Consolidation

The dependencies have been consolidated from multiple files:
- `backend/requirements.txt`
- `RAG/requirements.txt`
- `backend/rag/requirements.txt`

If you need to work on a specific module only, you can still find the original requirements files in their respective directories, but the root `requirements.txt` contains all necessary dependencies for the entire project. 