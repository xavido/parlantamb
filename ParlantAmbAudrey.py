import streamlit as st
from openai import OpenAI
import json

# Configuració inicial de la pàgina
st.set_page_config(
    page_title="Xatbot d'Ocells",
    page_icon="🦜",
    layout="wide"
)

# Carregar configuració d'estudiants (en un cas real, això vindria d'una base de dades)
ESTUDIANTS = {
    "marc": {"font_size": "16px", "nom": "Marc"},
    "anna": {"font_size": "18px", "nom": "Anna"},
    "pau": {"font_size": "20px", "nom": "Pau"}
}


# Funció per aplicar estils personalitzats
def apply_custom_styles():
    st.markdown("""
        <style>
        .chat-text {
            font-size: %s;
        }
        .stApp {
            background-image: url('https://img.freepik.com/free-vector/hand-drawn-birds-background_23-2148778033.jpg');
            background-size: cover;
        }
        </style>
    """ % ESTUDIANTS.get(st.session_state.get('usuari', ''), {}).get('font_size', '16px'), unsafe_allow_html=True)


# Inicialització de l'estat de la sessió
if 'messages_by_user' not in st.session_state:
    st.session_state.messages_by_user = {}
if 'usuari' not in st.session_state:
    st.session_state.usuari = None

# Aplicar estils
apply_custom_styles()

# Selecció d'usuari
if not st.session_state.usuari:
    st.title("👋 Benvingut al Xatbot d'Ocells!")
    usuari = st.selectbox("Selecciona el teu nom:", list(ESTUDIANTS.keys()))
    if st.button("Començar"):
        st.session_state.usuari = usuari
        st.rerun()

else:
    # Mostrar interfície del xat
    st.title(f"🦜 Hola {ESTUDIANTS[st.session_state.usuari]['nom']}! Pregunta'm sobre els ocells!")

    # Inicialitzar missatges per l'usuari actual si no existeixen
    if st.session_state.usuari not in st.session_state.messages_by_user:
        st.session_state.messages_by_user[st.session_state.usuari] = []

    # Mostrar historial de missatges de l'usuari actual
    for message in st.session_state.messages_by_user[st.session_state.usuari]:
        with st.chat_message(message["role"]):
            if "image_url" in message:
                st.image(message["image_url"])
            st.markdown(f"<div class='chat-text'>{message['content']}</div>", unsafe_allow_html=True)

    # Input de l'usuari
    if prompt := st.chat_input("Fes la teva pregunta sobre ocells..."):
        # Afegir missatge de l'usuari
        st.session_state.messages_by_user[st.session_state.usuari].append({"role": "user", "content": prompt})

        # Crear client OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Preparar el missatge del sistema
        system_prompt = """Ets un expert en ocells i només pots respondre preguntes relacionades amb ocells. 
        Si et pregunten sobre altres temes, has de dir amablement que només pots parlar d'ocells. 
        Adapta el llenguatge per nens de primària."""

        # Preparar tots els missatges
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(st.session_state.messages_by_user[st.session_state.usuari])

        # Obtenir resposta
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": m["role"], "content": m["content"]} for m in messages]
        )

        assistant_response = response.choices[0].message.content

        # Si la resposta menciona una imatge, generar-la
        if "imatge" in prompt.lower() or "dibuix" in prompt.lower():
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=f"Una imatge realista d'un ocell en base a aquesta descripció: {prompt}",
                size="1024x1024",
                n=1
            )
            image_url = image_response.data[0].url
            st.session_state.messages_by_user[st.session_state.usuari].append({
                "role": "assistant",
                "content": assistant_response,
                "image_url": image_url
            })
        else:
            st.session_state.messages_by_user[st.session_state.usuari].append({
                "role": "assistant",
                "content": assistant_response
            })

        st.rerun()

    # Botó per reiniciar el xat
    if st.button("Reiniciar xat"):
        st.session_state.messages_by_user[st.session_state.usuari] = []
        st.rerun() 