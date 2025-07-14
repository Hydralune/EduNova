@echo off
title 启动 EduNova 项目

:: 启动前端 PowerShell
start "EduNova Frontend" powershell -NoExit -Command "cd 'C:\Users\Ylon\Desktop\EduNova\frontend'; npm run dev"

:: 启动后端 PowerShell
start "EduNova Backend" powershell -NoExit -Command "cd 'C:\Users\Ylon\Desktop\EduNova\backend';conda activate edunova; python run.py"

exit
