import streamlit as st
from model import get_best_answer
import speech_recognition as sr

st.set_page_config(
    page_title="Chatbot USMBA",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé modifié
st.markdown("""
<style>
    :root {
        --primary: #2c3e50;
        --secondary: #2ecc71;  /* Couleur verte principale */
        --background: #f8f9fa;
    }

    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        height: 95vh;
        display: flex;
        flex-direction: column;
        background: var(--background);
        font-family: 'Segoe UI', sans-serif;
    }

    .header {
        text-align: center;
        margin-bottom: 20px;
        padding: 25px;
        background: linear-gradient(135deg, var(--primary) 0%, #2980b9 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        margin: 15px 0;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .message {
        margin-bottom: 20px;
        animation: fadeIn 0.3s;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background: var(--secondary);
        color: white;
        border-radius: 20px 20px 5px 20px;
        padding: 12px 18px;
        margin-left: 25%;
    }

    .bot-message {
        background: #ecf0f1;
        color: #2c3e50;
        border-radius: 20px 20px 20px 5px;
        padding: 12px 18px;
        margin-right: 25%;
    }

    .input-group {
        display: flex;
        gap: 10px;
        padding: 15px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
    }

    .mic-button {
        background: var(--secondary) !important;
        color: white !important;
        transition: all 0.2s ease;
    }

    button[kind="primary"] {
        background: var(--secondary) !important;
        border-color: var(--secondary) !important;
        transition: all 0.2s ease;
    }

    button[kind="primary"]:hover, .mic-button:hover {
        background: #27ae60 !important;
        border-color: #27ae60 !important;
        transform: scale(1.05);
    }

    /* Custom green radio buttons */
    .stRadio [role=radiogroup] {
        align-items: center;
        gap: 1rem;
    }
    
    .stRadio [role=radio] {
        border: 2px solid #2ecc71;
    }
    
    .stRadio [role=radio][aria-checked=true] {
        background-color: #2ecc71;
        border-color: #2ecc71;
    }
    
    .stRadio [role=radio][aria-checked=true] + div {
        color: #2ecc71;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def init_session():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'input_field' not in st.session_state:
        st.session_state.input_field = ""

def speech_to_text(lang='fr-FR'):
    """Reconnaissance vocale avec gestion de langue"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎙️ Parlez maintenant...")
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        return r.recognize_google(audio, language=lang)
    except sr.UnknownValueError:
        st.warning("Discours non reconnu")
    except sr.RequestError as e:
        st.error(f"Erreur du service : {str(e)}")
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
    return ""

# Initialisation
init_session()

# Interface
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# En-tête
with st.container():
    st.markdown("""
    <div class="header">
        <h1> Chatbot USMBA</h1>
        <p>Assistant intelligent pour les questions fréquentes</p>
    </div>
    """, unsafe_allow_html=True)

# Sélecteur de langue
lang = st.radio("Langue de reconnaissance vocale :", 
                ('Français', 'العربية'), 
                horizontal=True,
                key='lang_selector')

# Historique de chat
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d; padding: 40px 20px">
            <h4>Comment puis-je vous aider ?</h4>
            <p>Exemples de questions :</p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center">
                <div style="background: #e8f4fd; padding: 8px 16px; border-radius: 20px">
                    Dates d'inscription ?
                </div>
                <div style="background: #e8f4fd; padding: 8px 16px; border-radius: 20px">
                    Documents requis
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.history:
            if msg['sender'] == 'user':
                st.markdown(f'<div class="message user-message">{msg["text"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="message bot-message">{msg["text"]}</div>', 
                          unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Contrôles
with st.container():
    col1, col2 = st.columns([5, 1])
    
    with col1:
        question = st.text_input(
            "Entrez votre question",
            value=st.session_state.input_field,
            key="user_input",
            label_visibility="collapsed",
            placeholder="Écrivez ou cliquez sur le micro..."
        )
    
    with col2:
        if st.button("🎤", help="Activer le microphone", key="mic_btn"):
            lang_code = 'fr-FR' if st.session_state.lang_selector == 'Français' else 'ar-SA'
            spoken_text = speech_to_text(lang_code)
            if spoken_text:
                st.session_state.input_field = spoken_text
                st.rerun()
        
        if st.button("Envoyer", type="primary"):
            if question.strip():
                st.session_state.history.append({
                    'sender': 'user',
                    'text': question.strip()
                })
                
                with st.spinner("Recherche de la réponse..."):
                    response, _ = get_best_answer(question.strip())
                    
                    st.session_state.history.append({
                        'sender': 'bot',
                        'text': response
                    })
                
                st.session_state.input_field = ""
                st.rerun()

# Bouton de réinitialisation
if st.session_state.history:
    if st.button("Effacer l'historique", type="secondary"):
        st.session_state.history = []
        st.session_state.input_field = ""
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)