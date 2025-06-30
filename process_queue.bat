@echo off
echo EduNova - RAG Knowledge Base Queue Processor
echo =============================================
echo.

python process_queue.py %*

echo.
echo Press any key to exit...
pause > nul 