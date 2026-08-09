# Regras do Repositório de Receitas 🍳

## Instruções para Criação e Processamento de Receitas

Sempre que o usuário solicitar a criação de uma receita a partir de um link (de site ou vídeo) ou descrição:
1. Use o subagente `recipe_creator` para pesquisar (se necessário), estruturar as informações seguindo o modelo [`templates/modelo-receita.md`](file:///D:/Projects_IA/Development/receitas_touso/templates/modelo-receita.md) e salvar o markdown em `receitas/`.
2. Em seguida, utilize o subagente `recipe_image_generator` para criar a imagem ilustrativa da receita culinária. A imagem deve ser salva em formato PNG na pasta `imagens/` e nomeada com um UUID gerado aleatoriamente (ex: `imagens/f73e7218-18e3-469b-8260-8ba2182c1619.png`).
3. Atualize o arquivo markdown da receita criada substituindo o caminho da imagem temporária pelo caminho da imagem gerada (`../imagens/[UUID].png`).
4. Por fim, adicione o link e o título da nova receita criada nas seções correspondentes do arquivo [`INDEX.md`](file:///D:/Projects_IA/Development/receitas_touso/INDEX.md).
