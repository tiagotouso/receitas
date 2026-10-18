@echo off
set "PYTHONIOENCODING=utf-8"
echo ========================================================
echo   Atualizando Indices do Livro de Receitas...
echo ========================================================
"D:\My Project\IA-Assistentes\.venv\Scripts\python.exe" -X utf8 "D:\My Project\IA-Assistentes\.agents\skills\update-recipe-indices\scripts\gerar_indices.py" --readme
if "%1"=="--no-pause" goto fim
echo.
pause
:fim
