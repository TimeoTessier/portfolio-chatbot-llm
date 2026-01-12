"""
Application Streamlit pour le Portfolio Interactif de Timéo Tessier
Interface de chat avec un agent IA qui connaît tout le profil professionnel
"""

import streamlit as st
import asyncio
from agent import create_portfolio_agent, LAST_SOURCES_USED
from agents import Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded, ModelBehaviorError, AgentsException

# Configuration de la page
st.set_page_config(
    page_title="Portfolio Interactif - Timéo Tessier",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS personnalisé - Thème Noir Classique 🖤
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* ANIMATIONS SUBTILES */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* BACKGROUND PRINCIPAL */
    .main {
        max-width: 900px;
        background: #0a0a0a;
        font-family: 'Inter', sans-serif;
    }
    
    /* MESSAGES DE CHAT */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.5rem;
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        animation: fadeInUp 0.4s ease-out;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        border-color: #3a3a3a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        transform: translateY(-2px);
    }
    
    [data-testid="stChatMessageContent"] {
        background-color: transparent;
    }
    
    /* BADGES DES SOURCES */
    .source-badge {
        display: inline-block;
        background: #2a2a2a;
        color: #d1d5db;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.35rem;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #3a3a3a;
        transition: all 0.3s ease;
    }
    
    .source-badge:hover {
        background: #3a3a3a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid #2a2a2a;
    }
    
    /* TITRES */
    h1 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #e5e7eb !important;
        font-weight: 600;
    }
    
    h3 {
        color: #d1d5db !important;
        font-weight: 500;
    }
    
    /* INPUT DE CHAT */
    [data-testid="stChatInput"] {
        background: #1a1a1a;
        border: 1.5px solid #2a2a2a;
        border-radius: 0.8rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #3a3a3a;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
    }
    
    /* DÉSACTIVATION TRAIT ROUGE */
    textarea,
    input[type="text"],
    [contenteditable="true"] {
        -webkit-text-decoration-line: none !important;
        text-decoration-line: none !important;
        -webkit-text-decoration-color: transparent !important;
        text-decoration-color: transparent !important;
    }
    
    /* BOUTONS DE SUGGESTIONS */
    .stButton button {
        background: #1a1a1a;
        color: #e5e7eb;
        border: 1px solid #2a2a2a;
        border-radius: 0.8rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .stButton button:hover {
        background: #2a2a2a;
        border-color: #3a3a3a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    .stButton button:active {
        transform: translateY(0px);
    }
    
    /* BOUTONS DE TÉLÉCHARGEMENT */
    .stDownloadButton button {
        background: #1a1a1a;
        color: #e5e7eb;
        border: 1px solid #2a2a2a;
        border-radius: 0.8rem;
        font-weight: 600;
        width: 100%;
        margin-bottom: 0.8rem;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton button:hover {
        background: #2a2a2a;
        border-color: #3a3a3a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* MÉTRIQUES */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75rem !important;
    }
    
    /* TEXTE GÉNÉRAL */
    p, span, div, li {
        color: #e5e7eb;
    }
    
    /* LIENS */
    a {
        color: #d1d5db !important;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #ffffff !important;
    }
    
    /* FOOTER */
    footer {
        background: #0a0a0a;
        color: #6b7280;
        border-top: 1px solid #2a2a2a;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2a2a2a;
        border-radius: 5px;
        border: 2px solid #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3a3a3a;
    }
    
    /* MARKDOWN */
    .stMarkdown {
        color: #e5e7eb;
    }
    
    /* CODE BLOCKS */
    code {
        background: #1a1a1a;
        color: #d1d5db;
        padding: 0.3rem 0.6rem;
        border-radius: 0.4rem;
        border: 1px solid #2a2a2a;
        font-family: 'Fira Code', monospace;
    }
    
    /* SPINNER */
    .stSpinner > div {
        border-color: #ffffff !important;
        border-right-color: transparent !important;
    }
    
    /* DIVIDERS */
    hr {
        border: none;
        height: 1px;
        background: #2a2a2a;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Titre de l'application
st.title("💼 Portfolio Interactif")
st.markdown("### Découvrez le profil de Timéo Tessier")
st.markdown("Posez-moi des questions sur mon parcours, mes compétences, mes projets ou mes passions !")

# Sidebar avec informations
with st.sidebar:
    st.header("À propos")
    st.markdown("""
    **Timéo Tessier**  
    Étudiant en BUT Science des Données  
    Alternant Analyste BI chez SMACL
    
    ---
    
    ### 📄 Documents à télécharger
    """)
    
    # Téléchargement du CV
    with open("cv/CV tessier timeo.pdf", "rb") as file:
        st.download_button(
            label="📥 Télécharger mon CV",
            data=file,
            file_name="CV_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Téléchargement du Bilan 1ère année
    with open("cv/Bilan personnel -Tessier Timéo - 1ere_annee.pdf", "rb") as file:
        st.download_button(
            label="📥 Bilan Personnel 1ère année",
            data=file,
            file_name="Bilan_Personnel_1ere_annee_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Téléchargement du Bilan 2ème année
    with open("cv/Bilan personnel - Tessier Timéo.pdf", "rb") as file:
        st.download_button(
            label="📥 Bilan Personnel 2ème année",
            data=file,
            file_name="Bilan_Personnel_2eme_annee_Timeo_Tessier.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown("""
    ---
    
    ### Questions suggérées
    - Qui es-tu ?
    - Quelles sont tes compétences ?
    - Parle-moi de tes projets
    - Quel est ton parcours de formation ?
    - Quelles sont tes passions ?
    - Quel est ton style de travail ?
    
    ---
    
    ### Statistiques
    """)
    
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    st.metric("Messages échangés", st.session_state.message_count)
    
    if st.button("🗑️ Effacer l'historique"):
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
    avatar = "img/robot.avif" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # Afficher les sources si disponibles
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            st.markdown("**📚 Sources :**")
            sources_html = " ".join([f'<span class="source-badge">{source}</span>' for source in message["sources"]])
            st.markdown(sources_html, unsafe_allow_html=True)

# Suggestions de questions (affichées seulement si l'historique est vide)
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Questions suggérées")
    
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
            if st.button(f"💬 {suggestion}", key=f"suggestion_{idx}", use_container_width=True):
                # Mettre la suggestion dans le session_state pour la traiter
                st.session_state.pending_prompt = suggestion
                st.rerun()
    
    st.markdown("---")

# Zone de saisie du message - avec désactivation maximale du correcteur orthographique
prompt = st.chat_input("💬 Posez-moi une question sur mon profil...", key="chat_input")

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
    
    # Générer la réponse de l'assistant
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
                st.markdown("**📚 Sources :**")
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
            error_msg = "⚠️ Désolé, le traitement de votre question a pris trop de temps. Pouvez-vous reformuler ?"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        
        except ModelBehaviorError:
            error_msg = "⚠️ Une erreur s'est produite lors du traitement de votre question. Pouvez-vous réessayer ?"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        
        except AgentsException as e:
            error_msg = f"⚠️ Erreur de l'agent : {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        
        except Exception as e:
            error_msg = f"❌ Une erreur inattendue s'est produite : {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    💼 Portfolio Interactif - Timéo Tessier<br>
    Propulsé par OpenAI GPT-4.1-nano et Upstash Vector
</div>
""", unsafe_allow_html=True)
