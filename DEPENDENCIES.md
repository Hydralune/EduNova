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

## 打包依赖

打包EduNova为可执行文件需要以下依赖:

- PyInstaller: `pip install pyinstaller`
- 其他项目依赖（见上文）

### 打包环境要求

- Python 3.8+ (推荐3.9或3.10)
- Node.js 14+ (推荐16或18)
- 足够的磁盘空间（至少1GB用于构建过程）
- 足够的内存（至少4GB）

### 可能的打包问题及解决方案

1. **找不到模块**：如果打包过程中报错找不到某个模块，请确保该模块已安装并添加到`hidden-imports`中
   ```python
   # 在setup.py中添加
   "--hidden-import=模块名称"
   ```

2. **资源文件丢失**：如果打包后运行时缺少某些资源文件，请确保在`--add-data`参数中正确添加
   ```python
   # 在setup.py中添加
   "--add-data=源路径;目标路径"
   ```

3. **打包后运行崩溃**：尝试使用`--debug=all`参数重新打包，查看详细错误信息
   ```python
   # 在setup.py中添加
   "--debug=all"
   ``` 