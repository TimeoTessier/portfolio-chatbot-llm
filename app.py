"""
Application Streamlit pour le Portfolio Interactif de Timéo Tessier
Interface de chat avec un agent IA qui connaît tout le profil professionnel
"""

import streamlit as st
import asyncio
from src.agent import create_portfolio_agent, LAST_SOURCES_USED
from agents import Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded, ModelBehaviorError, AgentsException


# Configuration de la page
st.set_page_config(
    page_title="Portfolio Interactif - Timéo Tessier",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Minimal white theme CSS
st.markdown("""
<style>
  body { background: #ffffff; color: #000000; font-family: Arial, Helvetica, sans-serif; }
  .main { max-width: 900px; margin: auto; }
  .stButton button, .stDownloadButton button { border-radius: 6px; }
  .source-badge { display:inline-block; padding:4px 8px; border-radius:4px; background:#f0f0f0; color:#111; }
</style>
""", unsafe_allow_html=True)

# Titre de l'application
st.title("Portfolio Interactif")
st.markdown("### Découvrez le profil de Timéo Tessier")
st.markdown("Posez une question ou consultez les documents disponibles dans la barre latérale.")

# Sidebar avec informations
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    **Timéo Tessier**  
    Étudiant en BUT Science des Données  
    Alternant Analyste BI chez SMACL
    
    ---
    
    Documents à télécharger
    """)
    
    # Téléchargement du CV
    with open("cv/CV tessier timeo.pdf", "rb") as file:
        st.download_button(
            label="Télécharger mon CV",
            data=file,
            file_name="CV_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Téléchargement du Bilan 1ère année
    with open("cv/Bilan personnel -Tessier Timéo - 1ere_annee.pdf", "rb") as file:
        st.download_button(
            label="Bilan Personnel 1ère année",
            data=file,
            file_name="Bilan_Personnel_1ere_annee_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Téléchargement du Bilan 2ème année
    with open("cv/Bilan personnel - Tessier Timéo.pdf", "rb") as file:
        st.download_button(
            label="Bilan Personnel 2ème année",
            data=file,
            file_name="Bilan_Personnel_2eme_annee_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown("""
    ---
    
    Questions suggérées
    - Qui es-tu ?
    - Quelles sont tes compétences ?
    - Parle-moi de tes projets
    - Quel est ton parcours de formation ?
    - Quelles sont tes passions ?
    - Quel est ton style de travail ?
    
    ---
    
    Statistiques
    """)
    
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    st.metric("Messages échangés", st.session_state.message_count)
    
    if st.button("Effacer l'historique"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.session_id = f"streamlit_{id(st.session_state)}"
        st.rerun()

# Initialisation de l'état de session
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agent' not in st.session_state:
    st.session_state.agent = create_portfolio_agent()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit_{id(st.session_state)}"

# Afficher l'historique des messages
for message in st.session_state.messages:
    avatar = "img/robot.avif" if message.get("role") == "assistant" else None
    with st.chat_message(message.get("role", "user"), avatar=avatar):
        st.markdown(message.get("content", ""))

        # Afficher les sources si disponibles
        if message.get("role") == "assistant" and "sources" in message and message["sources"]:
            st.markdown("**Sources :**")
            sources_html = " ".join([f'<span class="source-badge">{source}</span>' for source in message["sources"]])
            st.markdown(sources_html, unsafe_allow_html=True)

# Suggestions de questions (affichées seulement si l'historique est vide)
if len(st.session_state.messages) == 0:
    st.markdown("### Questions suggérées")
    
    suggestions = [
        "Quel est ton parcours académique ?",
        "Quelles sont tes compétences techniques ?",
        "Parle-moi de ton expérience en alternance",
        "Quels projets as-tu réalisés ?",
        "Quels sont tes centres d'intérêt ?"
    ]
    
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx % 2]:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()

    st.markdown("---")

# Zone de saisie du message - avec désactivation maximale du correcteur orthographique
prompt = st.chat_input("Posez une question sur mon profil...", key="chat_input")

# Récupérer le prompt depuis les suggestions si disponible
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

# Traiter le prompt (qu'il vienne de l'input ou des suggestions)
if prompt:
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1

    # Afficher le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)

    # Générer la réponse de l'assistant via l'agent
    with st.chat_message("assistant", avatar="img/robot.avif"):
        message_placeholder = st.empty()

        try:
            # Créer la session pour l'historique
            session = SQLiteSession(st.session_state.session_id)

            # Exécuter l'agent de manière asynchrone
            async def get_response():
                result = await Runner.run(
                    st.session_state.agent,
                    prompt,
                    session=session
                )
                return result

            # Exécuter la coroutine
            result = asyncio.run(get_response())

            # Afficher la réponse
            response = result.final_output
            message_placeholder.markdown(response)

            # Récupérer et afficher les sources
            sources = LAST_SOURCES_USED.copy() if LAST_SOURCES_USED else []

            if sources:
                st.markdown("**Sources :**")
                sources_html = " ".join([f'<span class="source-badge">{source}</span>' for source in sources])
                st.markdown(sources_html, unsafe_allow_html=True)

            # Ajouter la réponse à l'historique
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": sources
            })
            st.session_state.message_count += 1

        except MaxTurnsExceeded:
            error_msg = "Désolé, le traitement de votre question a pris trop de temps. Pouvez-vous reformuler ?"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})

        except ModelBehaviorError:
            error_msg = "Une erreur s'est produite lors du traitement de votre question. Pouvez-vous réessayer ?"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})

        except AgentsException as e:
            error_msg = f"Erreur de l'agent : {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})

        except Exception as e:
            error_msg = f"Une erreur inattendue s'est produite : {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Portfolio Interactif - Timéo Tessier
</div>
""", unsafe_allow_html=True)
