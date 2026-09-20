@echo off
rem ==============================================================
rem   Atualizador Automático de Índices de Receitas
rem ==============================================================

chcp 65001 > nul
set "PYTHONIOENCODING=utf-8"

set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [AVISO] Interpretador do ambiente virtual nao encontrado em:
    echo "%PYTHON_EXE%"
    echo Tentando usar python padrao do sistema...
    set "PYTHON_EXE=python"
)

echo Executando gerador de indices...
echo.
"%PYTHON_EXE%" "%~dp0gerar_indices.py" --readme %*

if "%1"=="--no-pause" goto fim
echo.
pause
:fim
