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

# CSS personnalisé - Thème Noir & Violet
st.markdown("""
    <style>
    /* Thème noir et violet */
    .main {
        max-width: 800px;
        background-color: #0a0a0f;
    }
    
    /* Messages de chat */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        background-color: #141420;
        border: 1px solid #2d2d45;
    }
    
    /* Messages utilisateur */
    [data-testid="stChatMessageContent"] {
        background-color: transparent;
    }
    
    /* Badges des sources - violet */
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6b46c1 0%, #9333ea 100%);
        color: #ffffff;
        padding: 0.3rem 0.6rem;
        border-radius: 0.4rem;
        margin: 0.25rem;
        font-size: 0.8rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(147, 51, 234, 0.3);
    }
    
    /* Sidebar - thème noir */
    [data-testid="stSidebar"] {
        background-color: #0a0a0f;
        border-right: 1px solid #2d2d45;
    }
    
    /* Titre principal - violet */
    h1 {
        color: #a78bfa !important;
        text-shadow: 0 0 20px rgba(167, 139, 250, 0.3);
    }
    
    h2 {
        color: #c4b5fd !important;
    }
    
    h3 {
        color: #9ca3af !important;
    }
    
    /* Input de chat */
    [data-testid="stChatInput"] {
        background-color: #141420;
        border: 2px solid #6b46c1;
        border-radius: 0.8rem;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #9333ea;
        box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.2);
    }
    
    /* CORRECTION DÉFINITIVE DU TRAIT ROUGE */
    textarea,
    input[type="text"],
    [contenteditable="true"] {
        -webkit-text-decoration-line: none !important;
        text-decoration-line: none !important;
        -webkit-text-decoration-color: transparent !important;
        text-decoration-color: transparent !important;
        -webkit-text-decoration-style: none !important;
        text-decoration-style: none !important;
    }
    
    *::-webkit-input-placeholder,
    *:-moz-placeholder,
    *::-moz-placeholder,
    *:-ms-input-placeholder {
        -webkit-text-decoration-line: none !important;
        text-decoration-line: none !important;
    }
    
    /* Boutons - violet */
    .stButton button {
        background: linear-gradient(135deg, #6b46c1 0%, #9333ea 100%);
        color: #ffffff;
        border: none;
        border-radius: 0.6rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(147, 51, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.5);
        transform: translateY(-2px);
    }
    
    /* Boutons de téléchargement */
    .stDownloadButton button {
        background: linear-gradient(135deg, #6b46c1 0%, #9333ea 100%);
        color: #ffffff;
        border: none;
        border-radius: 0.6rem;
        font-weight: 500;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        transform: translateY(-2px);
    }
    
    /* Métriques - violet */
    [data-testid="stMetricValue"] {
        color: #a78bfa !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
    }
    
    /* Texte général */
    p, span, div, li {
        color: #e5e7eb;
    }
    
    /* Liens - violet */
    a {
        color: #a78bfa !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #c4b5fd !important;
    }
    
    /* Footer */
    footer {
        background-color: #0a0a0f;
        color: #6b7280;
        border-top: 1px solid #2d2d45;
    }
    
    /* Scrollbar personnalisée - violet */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6b46c1 0%, #9333ea 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #7c3aed 0%, #a855f7 100%);
    }
    
    /* Markdown - amélioration */
    .stMarkdown {
        color: #e5e7eb;
    }
    
    /* Code blocks */
    code {
        background-color: #1f1f2e;
        color: #a78bfa;
        padding: 0.2rem 0.4rem;
        border-radius: 0.3rem;
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Afficher les sources si disponibles
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            st.markdown("**📚 Sources :**")
            sources_html = " ".join([f'<span class="source-badge">{source}</span>' for source in message["sources"]])
            st.markdown(sources_html, unsafe_allow_html=True)

# Zone de saisie du message - avec désactivation maximale du correcteur orthographique
if prompt := st.chat_input("💬 Posez-moi une question sur mon profil...", key="chat_input"):
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1
    
    # Afficher le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer la réponse de l'assistant
    with st.chat_message("assistant"):
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
