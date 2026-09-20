"""
Script para geração e sincronização automática dos índices de receitas:
- receitas/INDEX_DOCES.md
- receitas/INDEX_SALGADOS.md
- receitas/INDEX_COMPLETO.md
- Outros índices que surgirem (ex: INDEX_BEBIDAS.md, INDEX_MASSAS.md, etc.)
- Opcionalmente atualiza a lista de receitas no README.md principal.

Uso:
    python gerar_indices.py [--readme] [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Garante suporte a UTF-8 no terminal Windows mesmo sem PYTHONIOENCODING explícito
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Configurações de diretórios
SCRIPT_DIR = Path(__file__).resolve().parent
RECEITAS_DIR = SCRIPT_DIR / "receitas"
README_PATH = SCRIPT_DIR / "README.md"


@dataclass
class Recipe:
    filename: str
    filepath: Path
    title: str
    display_title: str
    time_raw: str
    time_minutes: Optional[int]
    yield_raw: str
    categories_raw: str
    categories_list: List[str]
    difficulty: str
    tags: List[str]
    is_sweet: bool
    is_savory: bool
    is_baked: bool
    target_indices: Set[str] = field(default_factory=set)


# Definição e metadados de índices conhecidos (extensível)
INDEX_REGISTRY: Dict[str, Dict[str, str]] = {
    "INDEX_DOCES.md": {
        "title": "Subíndice de Receitas Doces 🍰",
        "description": "Aqui você encontra as receitas mais doces e guloseimas da nossa família.",
        "icon": "🍰",
    },
    "INDEX_SALGADOS.md": {
        "title": "Subíndice de Receitas Salgadas 🍕",
        "description": "Aqui você encontra os pratos principais salgados, assados, grelhados e acompanhamentos da nossa família.",
        "icon": "🍕",
    },
    "INDEX_BEBIDAS.md": {
        "title": "Subíndice de Bebidas e Drinques 🍹",
        "description": "Aqui você encontra sucos, drinques, chás e bebidas especiais da nossa família.",
        "icon": "🍹",
    },
    "INDEX_MASSAS.md": {
        "title": "Subíndice de Massas 🍝",
        "description": "Aqui você encontra massas artesanais, molhos e receitas italianas especiais.",
        "icon": "🍝",
    },
    "INDEX_ASSADOS.md": {
        "title": "Subíndice de Assados e Forno 🔥",
        "description": "Aqui você encontra receitas feitas com carinho no forno e assadeiras.",
        "icon": "🔥",
    },
}


def remove_accents(text: str) -> str:
    """Remove acentos de uma string para comparações insensíveis."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def clean_emojis(text: str) -> str:
    """Remove emojis de uma string mantendo letras, pontuação e números."""
    # Mantém caracteres padrão e acentuados, remove símbolos pictográficos
    cleaned = re.sub(r"[^\w\s\-\.,/()ºªáéíóúÁÉÍÓÚãõÃÕâêîôûÂÊÎÔÛàèìòùÀÈÌÒÙçÇ]", "", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def parse_minutes(time_str: str) -> Optional[int]:
    """Tenta converter strings como '40 minutos', '20 minutos (mais 3 horas de geladeira)' para minutos ativos inteiros."""
    # Se houver parênteses com tempo extra (geladeira, marinada, descanso), foca no tempo principal
    main_time_part = re.split(r"\(|\bmais\b", time_str, flags=re.I)[0]
    time_clean = remove_accents(main_time_part.lower())

    # Formato horas e minutos: '1 hora e 20 min'
    m_hm = re.search(r"(\d+)\s*h(?:ora)?(?:s)?(?:\s*e\s*|\s*)(\d+)?\s*m", time_clean)
    if m_hm:
        horas = int(m_hm.group(1))
        minutos = int(m_hm.group(2)) if m_hm.group(2) else 0
        return horas * 60 + minutos

    # Formato apenas horas: '2 horas'
    m_h = re.search(r"(\d+)\s*h(?:ora)?(?:s)?\b", time_clean)
    if m_h:
        return int(m_h.group(1)) * 60

    # Formato apenas minutos: '40 minutos' ou '25 min'
    m_m = re.search(r"(\d+)\s*m", time_clean)
    if m_m:
        return int(m_m.group(1))

    return None


def calculate_difficulty(recipe_content: str, minutes: Optional[int], categories: List[str]) -> str:
    """Calcula ou obtém a dificuldade da receita."""
    # Se especificado explicitamente no markdown
    m_diff = re.search(r"\*\*(?:Dificuldade):\*\*\s*([^\n\r]+)", recipe_content, re.I)
    if m_diff:
        val = m_diff.group(1).strip()
        val_lower = remove_accents(val.lower())
        if "facil" in val_lower:
            return "Fácil 🟢"
        if "med" in val_lower:
            return "Média 🟡"
        if "avan" in val_lower or "dificil" in val_lower:
            return "Avançada 🔴"
        return val

    # Regras por conteúdo e tags especiais
    content_lower = remove_accents(recipe_content.lower())
    if "aligot" in content_lower or "avancada" in content_lower:
        return "Avançada 🔴"

    # Heurística baseada no tempo ativo
    if minutes is not None:
        if minutes <= 40:
            return "Fácil 🟢"
        if minutes <= 60:
            return "Média 🟡"
        return "Média 🟡" if minutes <= 80 else "Avançada 🔴"

    return "Fácil 🟢"


def extract_recipe(filepath: Path) -> Recipe:
    """Lê um arquivo .md de receita e extrai todos os metadados necessários."""
    content = filepath.read_text(encoding="utf-8")

    # Título H1
    m_h1 = re.search(r"^#\s+(.+)$", content, re.M)
    raw_title = m_h1.group(1).strip() if m_h1 else filepath.stem
    # Remove marcação de rascunho/edição como 📝 do título de exibição se presente
    display_title = re.sub(r"\s*📝\s*$", "", raw_title).strip()

    # Tempo de preparo
    m_time = re.search(r"\*\*(?:Tempo de preparo|Tempo):\*\*\s*([^\n\r]+)", content, re.I)
    time_raw = m_time.group(1).strip() if m_time else "20 min"
    time_minutes = parse_minutes(time_raw)

    # Rendimento
    m_yield = re.search(r"\*\*Rendimento:\*\*\s*([^\n\r]+)", content, re.I)
    yield_raw = m_yield.group(1).strip() if m_yield else "4 porções"

    # Categorias
    m_cat = re.search(r"\*\*Categorias?:\*\*\s*([^\n\r]+)", content, re.I)
    cat_raw = m_cat.group(1).strip() if m_cat else ""
    cat_clean = clean_emojis(cat_raw)
    raw_cats = [c.strip() for c in cat_clean.split("/") if c.strip()]
    
    # Normalização de categorias para evitar repetições como Doce e Doces
    normalized_cats: List[str] = []
    for c in raw_cats:
        c_norm = "Doce" if remove_accents(c.lower()) in ["doce", "doces"] else ("Salgado" if remove_accents(c.lower()) in ["salgado", "salgados"] else c)
        if c_norm not in normalized_cats:
            normalized_cats.append(c_norm)

    # Índices referenciados no rodapé do próprio arquivo
    target_indices = set(re.findall(r"INDEX_[A-Z0-9_]+\.md", content, re.I))

    # Identificação se é Doce ou Salgado
    # Prioridade 1: links de rodapé explícitos
    has_sweet_link = "INDEX_DOCES.md" in target_indices
    has_savory_link = "INDEX_SALGADOS.md" in target_indices

    text_check = remove_accents(f"{cat_raw} {' '.join(normalized_cats)} {raw_title}").lower()

    if has_sweet_link and not has_savory_link:
        is_sweet = True
        is_savory = False
    elif has_savory_link and not has_sweet_link:
        is_sweet = False
        is_savory = True
    else:
        is_sweet = has_sweet_link or any(
            w in text_check for w in ["doce", "doces", "sobremesa", "bolo", "mousse", "bolacha"]
        )
        is_savory = has_savory_link or any(
            w in text_check for w in ["salgado", "salgados", "carne", "frango", "aves", "massa", "peixe", "suino"]
        )

    # Fallback se não detectou nenhum
    if not is_sweet and not is_savory:
        is_savory = True

    # Detecção se é Assado / Forno (título, categoria ou instruções no texto)
    full_text_lower = remove_accents(content.lower())
    is_baked = any(w in text_check for w in ["assado", "assada", "assadas", "forno", "bolo", "pao de queijo", "rosquinha"]) or (
        "forno" in full_text_lower and ("assar" in full_text_lower or "assadeira" in full_text_lower or "gratinar" in full_text_lower)
    )

    # Dificuldade
    difficulty = calculate_difficulty(content, time_minutes, normalized_cats)

    # Tags formatadas
    tags: List[str] = []
    # Tags manuais ou deduzidas
    if is_sweet:
        if any(w in text_check for w in ["bolo"]):
            tags.append("Bolo")
        if any(w in text_check for w in ["chocolate"]):
            tags.append("Chocolate")
        if any(w in text_check for w in ["gelado", "mousse"]):
            tags.append("Doce")
            tags.append("Gelado")
            tags.append("Sobremesa")
        if any(w in text_check for w in ["lanche"]):
            tags.append("Lanche")
        if any(w in text_check for w in ["queijo"]):
            tags.append("Queijo")
        if any(w in text_check for w in ["assado"]):
            tags.append("Assado")
        if any(w in text_check for w in ["frigideira"]):
            tags.append("Frigideira")
        if any(w in text_check for w in ["cafe"]):
            tags.append("Café da Manhã")
    else:
        if any(w in text_check for w in ["parmegiana", "classico", "macarrao", "nhoque"]):
            tags.append("Clássico")
        if any(w in text_check for w in ["carne", "fraldinha", "bife", "lombo", "moida"]):
            tags.append("Carne")
        if any(w in text_check for w in ["aves", "frango"]):
            tags.append("Aves")
        if any(w in text_check for w in ["massa", "macarrao", "lasanha", "nhoque"]):
            tags.append("Massa")
        if any(w in text_check for w in ["forno", "assado"]):
            tags.append("Forno")
        if any(w in text_check for w in ["pressao"]):
            tags.append("Pressão")
        if any(w in text_check for w in ["queijo", "aligot"]):
            tags.append("Queijo")
        if any(w in text_check for w in ["almoco"]):
            tags.append("Almoço de Domingo")
        if any(w in text_check for w in ["conforto"]):
            tags.append("Conforto")
        if any(w in text_check for w in ["especial"]):
            tags.append("Especial")
        if any(w in text_check for w in ["lanche"]):
            tags.append("Lanche")

    # Garante ao menos as categorias como tags se lista vazia
    if not tags:
        for c in normalized_cats:
            if c not in tags:
                tags.append(c)

    # Remove duplicadas mantendo a ordem
    tags_unique = list(dict.fromkeys(tags))

    return Recipe(
        filename=filepath.name,
        filepath=filepath,
        title=raw_title,
        display_title=display_title,
        time_raw=time_raw,
        time_minutes=time_minutes,
        yield_raw=yield_raw,
        categories_raw=cat_raw,
        categories_list=normalized_cats,
        difficulty=difficulty,
        tags=tags_unique,
        is_sweet=is_sweet,
        is_savory=is_savory,
        is_baked=is_baked,
        target_indices=target_indices,
    )


def load_all_recipes(directory: Path) -> List[Recipe]:
    """Carrega todas as receitas da pasta, ignorando arquivos de índice e outros não-receitas."""
    recipes: List[Recipe] = []
    for entry in sorted(directory.glob("*.md")):
        name = entry.name
        # Ignora índices e arquivos do sistema
        if name.startswith("INDEX_") or name.startswith(".") or name.lower() == "readme.md":
            continue
        try:
            recipes.append(extract_recipe(entry))
        except Exception as err:
            print(f"[AVISO] Erro ao ler {name}: {err}")

    # Ordena alfabeticamente pelo display_title
    recipes.sort(key=lambda r: remove_accents(r.display_title).lower())
    return recipes


def format_category_parentheses(recipe: Recipe, context: str = "doces") -> str:
    """Formata o texto dentro de '*(...)*' para os subíndices temáticos."""
    cats = [c for c in recipe.categories_list if c]
    if context == "doces":
        # Se não tiver 'Doce' no início, adiciona
        if not any(remove_accents(c.lower()) == "doce" for c in cats):
            cats.insert(0, "Doce")
    elif context == "salgados":
        # Se não tiver 'Salgado' no início, adiciona
        if not any(remove_accents(c.lower()) in ["salgado", "salgados"] for c in cats):
            cats.insert(0, "Salgado")

    # Limpa emojis e une com barra
    clean_cats = [clean_emojis(c) for c in cats]
    return " / ".join(dict.fromkeys(clean_cats))


def generate_index_doces(recipes: List[Recipe]) -> str:
    """Gera o markdown do INDEX_DOCES.md."""
    sweet_recipes = [r for r in recipes if r.is_sweet]

    lines = [
        "# Subíndice de Receitas Doces 🍰",
        "",
        "Aqui você encontra as receitas mais doces e guloseimas da nossa família.",
        "",
        "---",
        "",
    ]

    for r in sweet_recipes:
        cat_str = format_category_parentheses(r, context="doces")
        lines.append(f"- [{r.display_title}]({r.filename}) *({cat_str})*")

    lines.extend([
        "",
        "---",
        "",
        "[« Voltar para o Índice Geral](../README.md)",
        "",
    ])

    return "\n".join(lines)


def generate_index_salgados(recipes: List[Recipe]) -> str:
    """Gera o markdown do INDEX_SALGADOS.md."""
    savory_recipes = [r for r in recipes if r.is_savory]

    lines = [
        "# Subíndice de Receitas Salgadas 🍕",
        "",
        "Aqui você encontra os pratos principais salgados, assados, grelhados e acompanhamentos da nossa família.",
        "",
        "---",
        "",
    ]

    for r in savory_recipes:
        cat_str = format_category_parentheses(r, context="salgados")
        lines.append(f"- [{r.display_title}]({r.filename}) *({cat_str})*")

    lines.extend([
        "",
        "---",
        "",
        "[« Voltar para o Índice Geral](../README.md)",
        "",
    ])

    return "\n".join(lines)


def generate_index_completo(recipes: List[Recipe]) -> str:
    """Gera o markdown do INDEX_COMPLETO.md com tabela de busca rápida e seções."""
    lines = [
        "# Índice Completo e Tabela de Busca Rápida 📋",
        "",
        "Este índice reúne todas as receitas cadastradas na nossa cozinha, organizadas para facilitar a busca rápida e a seleção de pratos baseados no tempo e dificuldade.",
        "",
        "---",
        "",
        "## 🔍 Tabela de Busca Rápida",
        "",
        "| Prato | Categoria | Tempo | Dificuldade | Tags |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]

    # Preenchimento da Tabela
    for r in recipes:
        # Categoria formatada para tabela
        cat_icon = "🍰 Doce" if r.is_sweet else "🍕 Salgado"
        method = "🔥 Assado" if r.is_baked else ("❄️ Gelado" if "gelado" in remove_accents(r.categories_raw).lower() else "🍲 Outros")
        cat_display = f"{cat_icon} / {method}"

        # Tempo formatado
        tempo_str = f"{r.time_minutes} min ⏱️" if r.time_minutes else clean_emojis(r.time_raw).strip()
        if not tempo_str.endswith("⏱️"):
            tempo_str += " ⏱️"

        # Tags formatadas
        tags_display = " ".join(f"`[{t}]`" for t in r.tags[:4])

        lines.append(f"| [{r.display_title}]({r.filename}) | {cat_display} | {tempo_str} | {r.difficulty} | {tags_display} |")

    lines.extend(["", "---", "", "## 🍰 Doces", ""])
    for r in [x for x in recipes if x.is_sweet]:
        tags_str = " ".join(f"`[{t}]`" for t in r.tags[:3])
        lines.append(f"* **{r.display_title}** - [Ver Receita]({r.filename}) {tags_str}")

    lines.extend(["", "---", "", "## 🍕 Salgados", ""])
    for r in [x for x in recipes if x.is_savory]:
        tags_str = " ".join(f"`[{t}]`" for t in r.tags[:3])
        lines.append(f"* **{r.display_title}** - [Ver Receita]({r.filename}) {tags_str}")

    lines.extend(["", "---", "", "## 🔥 Assados", ""])
    for r in [x for x in recipes if x.is_baked]:
        tags_str = " ".join(f"`[{t}]`" for t in r.tags[:3])
        lines.append(f"* **{r.display_title}** - [Ver Receita]({r.filename}) {tags_str}")

    lines.extend(["", "---", "", "## 🍲 Outros (Cozidos, Fritos, Panela)", ""])
    for r in [x for x in recipes if not x.is_baked and not ("gelado" in remove_accents(x.categories_raw).lower())]:
        tags_str = " ".join(f"`[{t}]`" for t in r.tags[:3])
        lines.append(f"* **{r.display_title}** - [Ver Receita]({r.filename}) {tags_str}")

    lines.extend([
        "",
        "---",
        "",
        "📖 [« Voltar para o Índice Geral](../README.md)",
        "",
    ])

    return "\n".join(lines)


def generate_custom_index(index_filename: str, recipes: List[Recipe]) -> str:
    """Gera qualquer índice personalizado ou detectado dinamicamente."""
    meta = INDEX_REGISTRY.get(index_filename, {})
    title = meta.get("title")
    if not title:
        base_name = index_filename.replace("INDEX_", "").replace(".md", "").title()
        title = f"Subíndice de Receitas {base_name} 🍽️"

    description = meta.get(
        "description",
        f"Aqui você encontra receitas de {title.split()[-2].lower()} da nossa família."
    )

    matched_recipes: List[Recipe] = []
    name_clean = remove_accents(index_filename.lower())

    for r in recipes:
        # Se a receita aponta explicitamente para este índice
        if index_filename in r.target_indices:
            matched_recipes.append(r)
            continue
        # Ou se casa com o tema do índice
        if "bebida" in name_clean and any("bebida" in remove_accents(c.lower()) for c in r.categories_list):
            matched_recipes.append(r)
        elif "massa" in name_clean and any("massa" in remove_accents(c.lower()) for c in r.categories_list):
            matched_recipes.append(r)

    matched_recipes.sort(key=lambda x: remove_accents(x.display_title).lower())

    lines = [
        f"# {title}",
        "",
        description,
        "",
        "---",
        "",
    ]

    for r in matched_recipes:
        cat_str = " / ".join(clean_emojis(c) for c in r.categories_list if c)
        lines.append(f"- [{r.display_title}]({r.filename}) *({cat_str})*")

    lines.extend([
        "",
        "---",
        "",
        "[« Voltar para o Índice Geral](../README.md)",
        "",
    ])

    return "\n".join(lines)


def update_readme_recipes_section(readme_path: Path, recipes: List[Recipe], dry_run: bool = False) -> bool:
    """Atualiza a seção 'Lista Completa de Receitas (Acesso Direto)' do README.md."""
    if not readme_path.exists():
        print(f"[AVISO] {readme_path} não foi encontrado.")
        return False

    content = readme_path.read_text(encoding="utf-8")
    header_pattern = r"(## 🍽️ Lista Completa de Receitas \(Acesso Direto\)\s*\n+)([\s\S]*?)(\n---|\Z)"
    match = re.search(header_pattern, content)

    if not match:
        print("[AVISO] Seção de receitas não encontrada no README.md.")
        return False

    header = match.group(1)
    footer = match.group(3)

    new_list_lines: List[str] = []
    for r in recipes:
        tags_str = " ".join(f"`[{t}]`" for t in r.tags[:3])
        new_list_lines.append(f"* **{r.display_title}** - [Ver Receita](receitas/{r.filename}) {tags_str}")

    new_section_content = header + "\n".join(new_list_lines) + "\n\n" + footer
    new_full_content = content[:match.start()] + new_section_content + content[match.end():]

    if not dry_run:
        readme_path.write_text(new_full_content, encoding="utf-8")
        print(f"[OK] README.md atualizado com {len(recipes)} receitas.")
    else:
        print(f"[DRY-RUN] README.md seria atualizado com {len(recipes)} receitas.")

    return True


def discover_all_needed_indices(recipes: List[Recipe]) -> Set[str]:
    """Descobre todos os índices que precisam ser criados ou atualizados."""
    indices: Set[str] = {"INDEX_DOCES.md", "INDEX_SALGADOS.md", "INDEX_COMPLETO.md"}

    # Procura por outros índices mencionados no rodapé das receitas
    for r in recipes:
        for idx in r.target_indices:
            if idx.startswith("INDEX_") and idx.endswith(".md"):
                indices.add(idx)

    # Procura por arquivos INDEX_*.md já existentes na pasta receitas
    for p in RECEITAS_DIR.glob("INDEX_*.md"):
        indices.add(p.name)

    return indices


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera e atualiza os arquivos de índice das receitas.")
    parser.add_argument("--readme", action="store_true", help="Atualiza também a lista de receitas no README.md principal.")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem gravar alterações no disco.")
    parser.add_argument("--no-pause", action="store_true", help="Flag de controle usada por scripts batch.")
    args = parser.parse_args()

    print("==================================================")
    print("   🍳 Gerador Automático de Índices de Receitas   ")
    print("==================================================")

    if not RECEITAS_DIR.exists():
        print(f"[ERRO] Diretório de receitas não encontrado: {RECEITAS_DIR}")
        return

    recipes = load_all_recipes(RECEITAS_DIR)
    print(f"[INFO] {len(recipes)} receitas carregadas com sucesso.")

    needed_indices = discover_all_needed_indices(recipes)
    print(f"[INFO] Índices a processar: {', '.join(sorted(needed_indices))}")

    for idx_name in sorted(needed_indices):
        out_path = RECEITAS_DIR / idx_name

        if idx_name == "INDEX_DOCES.md":
            md_content = generate_index_doces(recipes)
        elif idx_name == "INDEX_SALGADOS.md":
            md_content = generate_index_salgados(recipes)
        elif idx_name == "INDEX_COMPLETO.md":
            md_content = generate_index_completo(recipes)
        else:
            md_content = generate_custom_index(idx_name, recipes)

        if not args.dry_run:
            out_path.write_text(md_content, encoding="utf-8")
            print(f"  [OK] Criado/Atualizado: {out_path.name}")
        else:
            print(f"  [DRY-RUN] Seria gravado: {out_path.name} ({len(md_content)} bytes)")

    if args.readme:
        update_readme_recipes_section(README_PATH, recipes, dry_run=args.dry_run)

    print("==================================================")
    print("   🎉 Processamento concluído com sucesso!        ")
    print("==================================================")


if __name__ == "__main__":
    main()
