"""
Script de découpage (chunking) des documents Markdown.
Ce script lit les fichiers .md du dossier data/ et les découpe en chunks cohérents
basés sur la structure hiérarchique des titres.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict

# Fix pour l'encodage Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def read_markdown_file(file_path: str) -> str:
    """Lit le contenu d'un fichier Markdown."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_markdown_sections(content: str, source_file: str) -> List[Dict[str, str]]:
    """
    Parse un fichier Markdown et le découpe en sections basées sur les titres.
    Chaque section conserve le contexte des titres parents.
    
    Args:
        content: Contenu du fichier Markdown
        source_file: Nom du fichier source (pour la traçabilité)
    
    Returns:
        Liste de dictionnaires contenant les chunks avec métadonnées
    """
    chunks = []
    lines = content.split('\n')
    
    current_chunk = []
    title_hierarchy = []  # Stack pour garder trace des titres parents
    current_metadata = {
        'source': source_file,
        'h1': '',
        'h2': '',
        'h3': ''
    }
    
    for line in lines:
        # Détection des titres
        if line.startswith('#'):
            # Si on a du contenu accumulé, on crée un chunk
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:  # Ne pas créer de chunks vides
                    chunks.append({
                        'text': chunk_text,
                        'metadata': current_metadata.copy()
                    })
                current_chunk = []
            
            # Déterminer le niveau du titre
            level = len(re.match(r'^#+', line).group())
            title_text = line.lstrip('#').strip()
            
            # Mettre à jour la hiérarchie
            if level == 1:
                current_metadata['h1'] = title_text
                current_metadata['h2'] = ''
                current_metadata['h3'] = ''
                title_hierarchy = [title_text]
            elif level == 2:
                current_metadata['h2'] = title_text
                current_metadata['h3'] = ''
                if len(title_hierarchy) >= 1:
                    title_hierarchy = title_hierarchy[:1] + [title_text]
                else:
                    title_hierarchy = [title_text]
            elif level == 3:
                current_metadata['h3'] = title_text
                if len(title_hierarchy) >= 2:
                    title_hierarchy = title_hierarchy[:2] + [title_text]
                else:
                    title_hierarchy.append(title_text)
            
            # Ajouter le titre au chunk avec contexte
            context_line = ' > '.join(title_hierarchy)
            current_chunk.append(f"**{context_line}**")
            current_chunk.append("")
        else:
            # Ajouter la ligne au chunk actuel
            current_chunk.append(line)
    
    # Ajouter le dernier chunk s'il existe
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append({
                'text': chunk_text,
                'metadata': current_metadata.copy()
            })
    
    return chunks


def chunk_markdown_files(data_folder: str = 'data') -> List[Dict[str, str]]:
    """
    Lit tous les fichiers Markdown du dossier data/ et les découpe en chunks.
    
    Args:
        data_folder: Chemin vers le dossier contenant les fichiers Markdown
    
    Returns:
        Liste de tous les chunks avec leurs métadonnées
    """
    all_chunks = []
    data_path = Path(data_folder)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Le dossier '{data_folder}' n'existe pas")
    
    # Lire tous les fichiers .md
    md_files = list(data_path.glob('*.md'))
    
    if not md_files:
        raise FileNotFoundError(f"Aucun fichier .md trouvé dans '{data_folder}'")
    
    print(f"📚 Traitement de {len(md_files)} fichiers Markdown...")
    
    for md_file in md_files:
        print(f"  📄 Lecture de {md_file.name}...")
        content = read_markdown_file(str(md_file))
        chunks = parse_markdown_sections(content, md_file.name)
        all_chunks.extend(chunks)
        print(f"    ✅ {len(chunks)} chunks créés")
    
    return all_chunks


def display_chunks_summary(chunks: List[Dict[str, str]]):
    """Affiche un résumé des chunks créés."""
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ DU CHUNKING")
    print(f"{'='*60}")
    print(f"Nombre total de chunks : {len(chunks)}")
    
    # Grouper par fichier source
    by_source = {}
    for chunk in chunks:
        source = chunk['metadata']['source']
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1
    
    print(f"\n📁 Répartition par fichier :")
    for source, count in sorted(by_source.items()):
        print(f"  • {source}: {count} chunks")
    
    # Statistiques sur la taille des chunks
    chunk_sizes = [len(chunk['text']) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    min_size = min(chunk_sizes) if chunk_sizes else 0
    max_size = max(chunk_sizes) if chunk_sizes else 0
    
    print(f"\n📏 Taille des chunks (caractères) :")
    print(f"  • Moyenne: {avg_size:.0f}")
    print(f"  • Minimum: {min_size}")
    print(f"  • Maximum: {max_size}")
    
    print(f"\n{'='*60}")


def display_sample_chunks(chunks: List[Dict[str, str]], n: int = 3):
    """Affiche quelques exemples de chunks."""
    print(f"\n📋 EXEMPLES DE CHUNKS (premiers {min(n, len(chunks))}) :")
    print(f"{'='*60}")
    
    for i, chunk in enumerate(chunks[:n], 1):
        print(f"\n🔹 Chunk #{i}")
        print(f"   Source: {chunk['metadata']['source']}")
        if chunk['metadata']['h1']:
            print(f"   H1: {chunk['metadata']['h1']}")
        if chunk['metadata']['h2']:
            print(f"   H2: {chunk['metadata']['h2']}")
        if chunk['metadata']['h3']:
            print(f"   H3: {chunk['metadata']['h3']}")
        print(f"\n   Contenu (premiers 200 caractères):")
        print(f"   {chunk['text'][:200]}...")
        print(f"   [{len(chunk['text'])} caractères au total]")
        print(f"{'-'*60}")


if __name__ == "__main__":
    try:
        # Découper les documents
        chunks = chunk_markdown_files('data')
        
        # Afficher les résultats
        display_chunks_summary(chunks)
        display_sample_chunks(chunks, n=5)
        
        print(f"\n✅ Chunking terminé avec succès !")
        print(f"💡 Les chunks sont prêts pour l'indexation dans Upstash Vector")
        
        # Optionnel : sauvegarder les chunks dans un fichier pour inspection
        import json
        with open('data/chunks_output.json', 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        print(f"📝 Les chunks ont été sauvegardés dans 'data/chunks_output.json' pour inspection")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
