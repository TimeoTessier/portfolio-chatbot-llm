import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from upstash_vector import Index

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'index Upstash Vector
upstash_index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)


@function_tool
def search_portfolio_data(query: str) -> str:
    """
    Recherche des informations dans la base de données vectorielle du portfolio.
    Utilisez cet outil pour trouver des informations précises sur Timéo :
    - Ses projets
    - Ses compétences techniques
    - Son parcours de formation
    - Ses expériences professionnelles
    - Ses centres d'intérêt
    
    Args:
        query: La question ou le sujet à rechercher
    
    Returns:
        Les informations pertinentes trouvées dans la base de données
    """
    try:
        # Rechercher dans la base vectorielle
        results = upstash_index.query(
            data=query,
            top_k=5,
            include_metadata=True
        )
        
        if not results:
            return "Aucune information trouvée pour cette question."
        
        # Formater les résultats
        formatted_results = []
        for i, result in enumerate(results, 1):
            content = result.metadata.get('content', '')
            source = result.metadata.get('source', 'N/A')
            score = result.score
            
            formatted_results.append(
                f"[Résultat {i} - Score: {score:.2f} - Source: {source}]\n{content}"
            )
        
        return "\n\n".join(formatted_results)
    
    except Exception as e:
        return f"Erreur lors de la recherche : {str(e)}"


def create_portfolio_agent() -> Agent:
    """
    Crée l'agent IA pour le portfolio interactif.
    Cet agent se comporte comme un jumeau virtuel professionnel.
    """
    
    agent = Agent(
        name="Portfolio Assistant",
        instructions="""
        Tu es Timéo Tessier, étudiant en deuxième année de BUT Science des Données à Niort.
        Tu es en alternance chez SMACL en tant qu'Analyste BI.
        
        Ton rôle est de répondre aux questions sur ton profil professionnel de manière naturelle et engageante.
        
        IMPORTANT : Pour toute question sur ton profil (projets, compétences, formation, expériences, passions),
        tu DOIS utiliser l'outil search_portfolio_data pour récupérer les informations précises depuis ta base de données.
        Ne te fie pas uniquement à ta mémoire - utilise TOUJOURS l'outil pour avoir des informations à jour et détaillées.
        
        Après avoir récupéré les informations, réponds de manière naturelle et conversationnelle à la première personne 
        ("je", "mon", "mes") comme si tu étais Timéo.
        
        Sois professionnel mais amical et accessible.
        Si l'outil ne trouve pas d'information, dis-le honnêtement.
        """,
        model="gpt-4.1-nano",
        tools=[search_portfolio_data],
    )
    
    return agent


async def test_agent():
    """
    Fonction de test asynchrone pour l'agent avec RAG
    """
    agent = create_portfolio_agent()
    
    # Questions de test qui nécessitent la recherche vectorielle
    test_questions = [
        "Qui es-tu ?",
        "Quelles sont tes compétences en SQL et Qlik Sense ?",
        "Parle-moi de ton projet sur les séries temporelles",
        "Quelle est ta passion pour le football ?",
        "Quel est ton parcours de formation ?",
        "Parle-moi de ton alternance chez SMACL",
    ]
    
    print("🤖 Test de l'agent Portfolio avec RAG")
    print("=" * 80)
    print()
    
    for question in test_questions:
        print(f"❓ Question : {question}")
        print("-" * 80)
        
        # Exécution asynchrone de l'agent
        result = await Runner.run(agent, question)
        
        print(f"💬 Réponse : {result.final_output}")
        print()
        print("=" * 80)
        print()


async def interactive_chat():
    """
    Mode chat interactif avec l'agent
    """
    agent = create_portfolio_agent()
    
    print("🤖 Chat interactif avec l'agent Portfolio")
    print("=" * 80)
    print("Tapez 'exit' ou 'quit' pour quitter")
    print()
    
    while True:
        user_input = input("Vous : ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Au revoir !")
            break
        
        if not user_input:
            continue
        
        print()
        result = await Runner.run(agent, user_input)
        print(f"Timéo : {result.final_output}")
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    # Choix du mode
    print("Choisissez le mode :")
    print("1. Test automatique")
    print("2. Chat interactif")
    choice = input("Votre choix (1 ou 2) : ").strip()
    
    if choice == "1":
        asyncio.run(test_agent())
    elif choice == "2":
        asyncio.run(interactive_chat())
    else:
        print("❌ Choix invalide")