@echo off
echo ===================================
echo EduNova 打包工具
echo ===================================

:: 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Python，请安装Python 3.8或更高版本
    exit /b 1
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Node.js，请安装Node.js 14或更高版本
    exit /b 1
)

:: 安装必要的Python包
echo 正在安装必要的Python包...
pip install pyinstaller flask flask-cors
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 安装Python包失败
    exit /b 1
)

:: 构建前端
echo 正在构建前端...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 前端依赖安装失败
    cd ..
    exit /b 1
)

call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 前端构建失败
    cd ..
    exit /b 1
)
cd ..

:: 执行PyInstaller打包
echo 正在打包应用...
python setup.py build_exe
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 打包失败
    exit /b 1
)

echo ===================================
echo 打包完成! 可执行文件位于 dist/EduNova.exe
echo =================================== 