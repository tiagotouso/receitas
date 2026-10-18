# Regras do Repositório de Receitas 🍳

## Instruções para Criação e Processamento de Receitas

Sempre que o usuário solicitar a criação de uma receita a partir de um link (site, blog ou vídeo), receita em texto ou descrição livre:

1. **Atuação com Postura de Chef (`recipe_creator`):**
   - Use o subagente `recipe_creator` para pesquisar, converter e estruturar a preparação com rigor técnico de chef (mise en place, proporções equilibradas, técnicas de cocção, segredos e dicas de variações).
   - Siga rigorosamente o modelo [`templates/modelo-receita.md`](file:///D:/My%20Project/IA-Assistentes/RECEITAS/templates/modelo-receita.md) e salve o arquivo markdown em `receitas/[nome-em-kebab-case].md`.

2. **Identidade Visual e Emojis:**
   - Garanta que o título principal e todas as seções da receita contenham **emojis temáticos** apropriados ao prato (ex: 🍖 para carne, 🌽 para milho, 🧀 para queijos, 🍫 para doces).

3. **Geração e Padronização da Imagem (`recipe_image_generator`):**
   - Utilize o subagente `recipe_image_generator` ou a skill `recipe-image-handler` para criar a imagem ilustrativa da receita culinária.
   - A imagem deve ser salva em formato PNG na pasta `imagens/` e nomeada com um **UUID v4** aleatório (ex: `imagens/f73e7218-18e3-469b-8260-8ba2182c1619.png`) com proporções de paisagem (800x500).
   - Atualize a referência no markdown substituindo a tag temporária pelo caminho relativo oficial (`../imagens/[UUID].png`).

4. **Sincronização Automática dos Índices (`recipe_manager`):**
   - Utilize o script da skill `update-recipe-indices` para atualizar automaticamente as seções do [`README.md`](file:///D:/My%20Project/IA-Assistentes/RECEITAS/README.md) (Índice Geral), bem como os subíndices temáticos (`receitas/INDEX_DOCES.md`, `receitas/INDEX_SALGADOS.md`, `receitas/INDEX_COMPLETO.md`).
   - Comando rápido:
     ```powershell
     $env:PYTHONIOENCODING="utf-8"; & "D:\My Project\IA-Assistentes\.venv\Scripts\python.exe" -X utf8 "D:\My Project\IA-Assistentes\.agents\skills\update-recipe-indices\scripts\gerar_indices.py" --readme
     ```

5. **Validação de Qualidade:**
   - Use o script de validação para checar se a receita atende a 100% das exigências:
     ```powershell
     & "D:\My Project\IA-Assistentes\.venv\Scripts\python.exe" "D:\My Project\IA-Assistentes\.agents\skills\recipe-tools\scripts\recipe_tools.py" validar
     ```
