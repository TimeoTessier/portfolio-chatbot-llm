import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, SQLiteSession
from agents.exceptions import MaxTurnsExceeded, ModelBehaviorError, AgentsException
from upstash_vector import Index

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'index Upstash Vector
upstash_index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

# Variable globale pour stocker les sources utilisées
LAST_SOURCES_USED = []
VERBOSE_MODE = False


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
    global LAST_SOURCES_USED
    LAST_SOURCES_USED = []
    
    try:
        # Augmenter top_k pour avoir plus de résultats
        top_k = 8
        
        if VERBOSE_MODE:
            print(f"  🔍 Recherche avec top_k={top_k}...")
        
        # Rechercher dans la base vectorielle
        results = upstash_index.query(
            data=query,
            top_k=top_k,
            include_metadata=True
        )
        
        if not results:
            return "Aucune information trouvée pour cette question."
        
        if VERBOSE_MODE:
            print(f"  ✅ {len(results)} résultats trouvés")
        
        # Formater les résultats et stocker les sources (sans filtrage strict)
        formatted_results = []
        sources_set = set()
        
        for i, result in enumerate(results, 1):
            content = result.metadata.get('content', '')
            source = result.metadata.get('source', 'N/A')
            score = result.score
            
            sources_set.add(source)
            
            formatted_results.append(
                f"[Résultat {i} - Score: {score:.2f} - Source: {source}]\n{content}"
            )
        
        # Stocker les sources pour affichage
        LAST_SOURCES_USED = list(sources_set)
        
        return "\n\n".join(formatted_results)
    
    except Exception as e:
        if VERBOSE_MODE:
            print(f"  ❌ Erreur : {str(e)}")
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
        
        RÈGLES IMPORTANTES :
        
        1. **Questions sur MON profil** : Utilise TOUJOURS l'outil search_portfolio_data pour récupérer des informations sur :
           - Mes compétences techniques (SQL, Python, Qlik, etc.)
           - Mon parcours de formation (BUT Science des Données)
           - Mes expériences professionnelles (alternance SMACL)
           - Mes projets (base de données, séries temporelles, etc.)
           - Mes passions (football, animés, musique)
           - Mon profil psychologique et style de travail
           - Toute autre information ME concernant
        
        2. **Documents disponibles** : Si quelqu'un demande mon CV ou mes bilans personnels, mentionne que ces documents
           sont disponibles au téléchargement dans la barre latérale (sidebar) de l'application.
           Tu peux dire : "Mon CV et mes bilans personnels sont disponibles en téléchargement dans la sidebar à gauche !"
        
        3. **Questions générales ou hors sujet** : N'utilise PAS l'outil search_portfolio_data.
           Réponds simplement de manière conversationnelle en tant que Timéo.
           Exemples : questions sur l'astronomie, la météo, des faits généraux, etc.
           Tu peux dire : "Je ne suis pas spécialiste en [sujet], mais je peux t'en parler brièvement..."
        
        4. **Recentrage sur le profil** : Si la question n'a rien à voir avec moi, réponds brièvement puis suggère
           de poser des questions sur mon profil professionnel.
        
        Après avoir récupéré les informations via l'outil, réponds de manière naturelle et conversationnelle 
        à la première personne ("je", "mon", "mes") comme si tu étais Timéo.
        
        Sois professionnel mais amical et accessible.
        """,
        model="gpt-4.1-nano",
        tools=[search_portfolio_data],
    )
    
    return agent


async def test_agent():
    """
    Fonction de test asynchrone pour l'agent avec RAG (version améliorée)
    """
    global VERBOSE_MODE
    VERBOSE_MODE = True  # Activer verbose pour les tests
    
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
    
    print("🤖 Test de l'agent Portfolio avec RAG (Version améliorée)")
    print("=" * 80)
    print()
    
    # Session pour les tests
    session = SQLiteSession("portfolio_test")
    
    for question in test_questions:
        print(f"❓ Question : {question}")
        print("-" * 80)
        
        try:
            # Exécution asynchrone de l'agent avec session
            result = await Runner.run(agent, question, session=session)
            
            print(f"💬 Réponse : {result.final_output}")
            
            # Afficher les sources
            if LAST_SOURCES_USED:
                print(f"📚 Sources : {', '.join(LAST_SOURCES_USED)}")
            
        except MaxTurnsExceeded as e:
            print(f"⚠️  Erreur : Nombre maximum de tours dépassé - {e}")
        except ModelBehaviorError as e:
            print(f"⚠️  Erreur : Comportement inattendu du modèle - {e}")
        except AgentsException as e:
            print(f"⚠️  Erreur de l'agent : {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")
        
        print()
        print("=" * 80)
        print()


async def interactive_chat():
    """
    Mode chat interactif avec l'agent (version améliorée)
    """
    global VERBOSE_MODE
    
    agent = create_portfolio_agent()
    
    print("🤖 Chat interactif avec l'agent Portfolio")
    print("=" * 80)
    print("Commandes : 'exit' pour quitter | 'verbose' pour activer/désactiver le mode debug | 'sources' pour voir les dernières sources")
    print()
    
    # Session pour sauvegarder l'historique
    session = SQLiteSession("portfolio_chat")
    
    while True:
        try:
            user_input = input("Vous : ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except EOFError:
            print("\n\n👋 Au revoir !")
            break
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Au revoir !")
            break
        
        if user_input.lower() == 'verbose':
            VERBOSE_MODE = not VERBOSE_MODE
            print(f"✅ Mode verbose {'activé' if VERBOSE_MODE else 'désactivé'}")
            continue
        
        if user_input.lower() == 'sources':
            if LAST_SOURCES_USED:
                print(f"📚 Dernières sources utilisées : {', '.join(LAST_SOURCES_USED)}")
            else:
                print("Aucune source utilisée pour l'instant")
            continue
        
        if not user_input:
            continue
        
        print()
        
        try:
            # Exécution avec session pour l'historique
            result = await Runner.run(agent, user_input, session=session)
            print(f"Timéo : {result.final_output}")
            
            # Afficher les sources si disponibles
            if LAST_SOURCES_USED and not VERBOSE_MODE:
                print(f"📚 Sources : {', '.join(LAST_SOURCES_USED)}")
            
        except MaxTurnsExceeded as e:
            print(f"⚠️  Nombre maximum de tours dépassé : {e}")
        except ModelBehaviorError as e:
            print(f"⚠️  Erreur de comportement du modèle : {e}")
        except AgentsException as e:
            print(f"⚠️  Erreur de l'agent : {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")
        
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    # Choix du mode
    print("🚀 Agent Portfolio - Version améliorée")
    print()
    print("Choisissez le mode :")
    print("1. Test automatique (avec mode verbose)")
    print("2. Chat interactif (avec historique + sources)")
    choice = input("Votre choix (1 ou 2) : ").strip()
    
    if choice == "1":
        asyncio.run(test_agent())
    elif choice == "2":
        asyncio.run(interactive_chat())
    else:
        print("❌ Choix invalide")