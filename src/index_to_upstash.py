import json
import os
from dotenv import load_dotenv
from upstash_vector import Index

# Charger les variables d'environnement
load_dotenv()

def index_chunks_to_upstash():
    """
    Charge les chunks depuis chunks_output.json et les indexe dans Upstash Vector
    """
    
    # Initialiser la connexion à Upstash
    index = Index(
        url=os.getenv("UPSTASH_VECTOR_REST_URL"),
        token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    )
    
    print("Connexion à Upstash établie")
    
    # Charger les chunks
    with open("data/chunks_output.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    print(f"{len(chunks)} chunks chargés depuis data/chunks_output.json")
    
    # Réinitialiser l'index (supprimer les anciennes données)
    print("Réinitialisation de l'index...")
    index.reset()
    
    # Préparer les données pour l'indexation
    vectors = []
    for i, chunk in enumerate(chunks):
        vector_data = {
            "id": f"chunk_{i}",
            "data": chunk["text"],  # Le texte du chunk
            "metadata": {
                "source": chunk["metadata"]["source"],
                "h1": chunk["metadata"].get("h1", ""),
                "h2": chunk["metadata"].get("h2", ""),
                "h3": chunk["metadata"].get("h3", ""),
                "content": chunk["text"]
            }
        }
        vectors.append(vector_data)
    
    # Indexer par lots de 100 (limite Upstash)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Indexé {min(i + batch_size, len(vectors))}/{len(vectors)} chunks")
    
    print(f"\nIndexation terminée : {len(chunks)} chunks indexés dans Upstash")

if __name__ == "__main__":
    index_chunks_to_upstash()