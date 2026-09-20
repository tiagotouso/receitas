# Regras do Repositório de Receitas 🍳

## Instruções para Criação e Processamento de Receitas

Sempre que o usuário solicitar a criação de uma receita a partir de um link (de site ou vídeo) ou descrição:
1. Use o subagente `recipe_creator` para pesquisar (se necessário), estruturar as informações seguindo o modelo [`templates/modelo-receita.md`](file:///D:/Projects_IA/Development/receitas_touso/templates/modelo-receita.md) e salvar o markdown em `receitas/`.
2. Garanta que o título e seções da receita contenham **emojis temáticos** apropriados ao prato (ex: 🍖 para carne, 🌽 para milho, etc.).
3. Em seguida, utilize o subagente `recipe_image_generator` para criar a imagem ilustrativa da receita culinária. A imagem deve ser salva em formato PNG na pasta `imagens/` e nomeada com um UUID gerado aleatoriamente (ex: `imagens/f73e7218-18e3-469b-8260-8ba2182c1619.png`) com proporções de paisagem (800x500).
4. Atualize o arquivo markdown da receita criada substituindo o caminho da imagem temporária pelo caminho da imagem gerada (`../imagens/[UUID].png`).
5. Adicione o link e o título da nova receita criada nas seções correspondentes do arquivo [`README.md`](file:///D:/Projects_IA/Development/receitas_touso/README.md) (Índice Geral), bem como no subíndice por tipo correspondente (ex: `receitas/INDEX_DOCES.md` ou `receitas/INDEX_SALGADOS.md`).

