@echo off
set "PYTHONIOENCODING=utf-8"
echo ========================================================
echo   Validando Conformidade das Receitas do Acervo...
echo ========================================================
"D:\My Project\IA-Assistentes\.venv\Scripts\python.exe" "D:\My Project\IA-Assistentes\.agents\skills\recipe-tools\scripts\recipe_tools.py" validar
if "%1"=="--no-pause" goto fim
echo.
pause
:fim
