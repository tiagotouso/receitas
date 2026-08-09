# Instruções dos Agentes de Receitas 🤖

Este documento serve como referência de como utilizar ou instruir os agentes automatizados no repositório.

## 🧑‍🍳 RecipeCreator (Criador de Receitas)
* **Objetivo**: Ler links de sites, vídeos (como YouTube) ou anotações livres e gerar o arquivo markdown estruturado na pasta `receitas/`.
* **Fluxo**:
  1. Lê o conteúdo original (extraindo os textos).
  2. Organiza o conteúdo seguindo o modelo de [`templates/modelo-receita.md`](file:///D:/Projects_IA/Development/receitas_touso/templates/modelo-receita.md).
  3. Salva a receita na pasta [`receitas/`](file:///D:/Projects_IA/Development/receitas_touso/receitas).

## 🎨 RecipeImageGenerator (Gerador de Imagens)
* **Objetivo**: Criar uma imagem apetitosa e fotográfica para a receita correspondente.
* **Fluxo**:
  1. Cria um prompt fotográfico otimizado de comida com base no nome do prato.
  2. Gera a imagem usando a inteligência artificial.
  3. Renomeia e salva a imagem utilizando um formato padronizado com UUID (ex: `imagens/[UUID].png`).
  4. Atualiza o link da imagem no markdown da receita criada.
