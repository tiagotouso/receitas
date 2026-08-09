@echo off
rem =======================================
rem   Enviando receitas para o GitHub...
rem =======================================

git add .

set commit_msg=Adiciona novas receitas de familia
set /p commit_msg="Digite a mensagem do commit (ou pressione Enter para usar a padrao): "

git commit -m "%commit_msg%"

echo.
echo Enviando alteracoes para o branch atual...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um problema ao enviar para o GitHub. Verifique sua conexao ou credenciais.
) else (
    echo.
    echo [SUCESSO] Receitas atualizadas no GitHub com sucesso!
)

echo.
pause
