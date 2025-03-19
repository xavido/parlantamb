import openai
import streamlit as st
import time
import mysql.connector
import base64
import requests
import ftplib
from streamlit_mic_recorder import mic_recorder,speech_to_text
from PIL import Image
from io import BytesIO


assistant_id = st.secrets["OPENAI_ASSISTANT"]
db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

creaName = "-"
font_size = 12
lesinstruccions="Contesta sempre en català i si al prompt de la pregunta especifico un altre idioma contesta en català i la mateixa resposta en l'idioma del prompt. Contesta com si fos un nen de 5 anys i, si pots, inclou un exemple. Al final sempre indica que la informació l'has de validar amb la profesora."
#standar alt
especials=""
#standar
especials3=""
#standar baix
especials4=""
#standar molt baix
especials5=""
#standar baix	bangla
especials6=""
#stàndar baix	anglès
especials7=""
#stàndar baix i imatge
especials8=""
especials9=""
client = openai
count = 0

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Parlant Amb Hipatia...Soc filòsofa, astrònoma i matemàtica.", page_icon="🪐")

openai.api_key = st.secrets["auto_pau"]

# standar baix
l1 = ['xdominguez', 'araluz','celia','mh_planetes','mh_asteroides','mh_satel','mh_estrelles']
# standar baix, audio i arab
l2 = ['mh_galaxies']
#standar baix
l3 = []
# standar molt baix, imatge i audio
l4 = []
# standar alt , imatge, audio
l5 = []
# standar alt, imatge, audio i lletra gran
l6 = []
# standar alt i castella
l7 = []
# standar alt, imatge, audio i lletra gran
l8 = []
l9 = []


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def disable():
    if nom != '' and ( nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
        especials = "Contesta sempre amb 1 paràgraf de 3 línies."
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    else:
        if nom != '':
            st.sidebar.write(":red[Aquest/a usuari/a no existeix]")
        if nom in l2:
            especials3 = "Contesta sempre amb 2 frases.Repeteix la mateixa resposta en àrab."
        if nom in l3:
            especials6="Contesta sempre amb 1 paràgrafs."
        if nom in l4:
            especials7="Contesta sempre amb 3 frases."
        if nom in l5:
            especials4="Contesta sempre amb 1 paràgraf."
        if nom in l6:
            especials4 = "Contesta sempre amb 3 paràgrafs."
        if nom in l7:
            especials5 = "Contesta sempre amb 3 paràgrafs. Repeteix la mateixa resposta en castellà."

def enable():
    if "disabled" in st.session_state and st.session_state.disabled == True:
        st.session_state.disabled = False
        st.session_state.messages = []  # Clear the chat history
        st.session_state.start_chat = False  # Reset the chat state
        st.session_state.thread_id = None


# Initialize disabled for form_submit_button to False
if "disabled" not in st.session_state:
    st.session_state.disabled = False

with st.sidebar.form("usuari_form"):
  nom = st.text_input("Escriu la teva identificació 👇",disabled=st.session_state.disabled, key=1)
  submit_button = st.form_submit_button(label="Iniciar Xat",disabled=st.session_state.disabled, on_click=disable)
  if nom in l1:
      especials = "Contesta sempre amb 2 frases."
  if nom in l2:
      especials3 = "Contesta sempre amb 2 frases.Repeteix la mateixa resposta en àrab."
  if nom in l3:
      especials6 = "Contesta sempre amb 1 paràgraf."
  if nom in l4:
      especials7 = "Contesta sempre amb 3 frases."
  if nom in l5:
      especials4 = "Contesta sempre amb 1 paràgraf."
  if nom in l6:
      especials4 = "Contesta sempre amb 3 paràgrafs."
  if nom in l7:
      especials5 = "Contesta sempre amb 3 paràgrafs. Repeteix la mateixa resposta en castellà."

  if submit_button and nom != '' and ( nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

# Simulamos que cada usuario tiene un tamaño de letra guardado
if "font_size" not in st.session_state:
    st.session_state["font_size"] = "16px"  # Tamaño por defecto

if nom in l6:
    font_size = "40px"

st.session_state["font_size"] = font_size

# Aplicamos CSS dinámico
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Parisienne&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    
    .lletralligada {
        font-family: 'Parisienne', cursive;
        font-size: 20px;
    }
    .lletraimprenta {
        font-family: 'Roboto';
        font-size: 20px;
        text-transform: uppercase;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.title("Parlant amb...Hipatia")
st.write("Soc filòsofa, astrònoma i matemàtica.")

st.sidebar.button("Sortir del Xat",on_click=enable)

if st.session_state.start_chat:

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if stt_user := speech_to_text(language='es', start_prompt="Fer pregunta amb veu",stop_prompt="Fi de la pregunta",use_container_width=True, just_once=True, key='STT'):
        prompt = stt_user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    if prompt := st.chat_input("Escriu aquí la teva pregunta") :

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
           
        if "imatge" in prompt.lower() or "dibuix" in prompt.lower()  or "foto" in prompt.lower() or "fotografia" in prompt.lower():
            with st.chat_message("assistant"):
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"Una imatge en base a aquesta descripció: {prompt} .",
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                # Desa la imatge a la sessió amb un format compatible
                image_data = requests.get(response.data[0].url)
                img = Image.open(BytesIO(image_data.content))

                #st.session_state["messages"].append({"role": "assistant", "content": img, "type": "image"})
                st.session_state["messages"].append({"role": "assistant", "content": response.data[0].url, "type": "image"})
                st.image(response.data[0].url, caption=prompt)


            resinfografria = requests.get(response.data[0].url)
            creaName = str(nom) + "_" + str(time.time()) + "_" + str(2025632632) + ".jpg"
            with open(creaName, 'wb') as f:
                f.write(resinfografria.content)

            ftp_server = ftplib.FTP(st.secrets["PA_FTP"], st.secrets["PA_FTPUSER"], st.secrets["PA_COD"])
            file = open(creaName, 'rb')  # file to send
            # Read file in binary mode
            ftp_server.storbinary('STOR ' + creaName, file)
            ftp_server.quit()
            file.close()  # close file and FTP
            # Crea una conexión con la base de datos
            conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                           password=db_password)

            # Crea un cursor para ejecutar comandos SQL
            cur = conn.cursor()

            # Ejecuta una consulta SQL
            sql = "INSERT INTO teclaPREGUNTES (idc,pregunta,infografia,tema,curso,topico) VALUES (%s,%s,%s,%s,%s,%s)"

            valores = (nom, prompt, creaName, 2025632632, 'PRI2', 'Univers')
            cur.execute(sql, valores)

            # Obtiene los resultados de la consulta
            results_database = cur.fetchall()
            conn.commit()

            # Cierra la conexión con la base de datos
            cur.close()
            conn.close()
        else:
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt+especials+especials3+especials4+especials5+especials6+especials7
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions=lesinstruccions+especials+especials3+especials4+especials5+especials6+especials7
            )

            while run.status != 'completed':
                #time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    resposta = message.content[0].text.value
                    #st.markdown(message.content[0].text.value)
                    st.markdown(f'<p class="lletraimprenta">{resposta}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="lletralligada">{resposta}</p>', unsafe_allow_html=True)
                    
                    if nom in l1 or nom in l2:
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos:" + resposta + ".",
                            size="1024x1024",
                            quality="standard",
                            n=1
                        )
                        st.image(response.data[0].url, caption=prompt)
                        resinfografria = requests.get(response.data[0].url)
                        creaName = str(nom) + "_" + str(time.time()) + "_" + str(2025632632) + ".jpg"
                        with open(creaName, 'wb') as f:
                            f.write(resinfografria.content)

                        ftp_server = ftplib.FTP(st.secrets["PA_FTP"], st.secrets["PA_FTPUSER"], st.secrets["PA_COD"])
                        file = open(creaName, 'rb')  # file to send
                        # Read file in binary mode
                        ftp_server.storbinary('STOR ' + creaName, file)
                        ftp_server.quit()
                        file.close()  # close file and FTP

                        # Crea una conexión con la base de datos
                        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                       password=db_password)

                        # Crea un cursor para ejecutar comandos SQL
                        cur = conn.cursor()

                        # Ejecuta una consulta SQL
                        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema,curso,topico) VALUES (%s,%s,%s,%s,%s,%s,%s)"

                        valores = (nom, prompt, message.content[0].text.value, creaName, 2025632632, 'PRI2', 'Univers')
                        cur.execute(sql, valores)

                        # Obtiene los resultados de la consulta
                        results_database = cur.fetchall()
                        conn.commit()

                        # Cierra la conexión con la base de datos
                        cur.close()
                        conn.close()

                        if nom in l2 or nom in l1:
                            client.beta.threads.messages.create(
                                thread_id=st.session_state.thread_id,
                                role="user",
                                content="Necessito que m'expliquis com un nen de 5 anys aquesta frase:"+resposta+".Pensa que el nen no té molt de vocabulari".
                            )
                
                            run = client.beta.threads.runs.create(
                                thread_id=st.session_state.thread_id,
                                assistant_id=assistant_id,
                                instructions=""
                            )
                
                            while run.status != 'completed':
                                #time.sleep(1)
                                run = client.beta.threads.runs.retrieve(
                                    thread_id=st.session_state.thread_id,
                                    run_id=run.id
                                )
                            messages = client.beta.threads.messages.list(
                                thread_id=st.session_state.thread_id
                            )
                
                            # Process and display assistant messages
                            assistant_messages_for_run = [
                                message for message in messages
                                if message.run_id == run.id and message.role == "assistant"
                            ]
                            response = ''
                            response = client.audio.speech.create(
                                model="tts-1",
                                voice="alloy",
                                input=message.content[0].text.value,
                            )
                            # response = message.content[0].text.value
                            elaudio = st.empty()
                            nomfitxer = "output_" + str(count) + "_" + "_" + nom + "_.mp3"
                            count += 1
                            response.stream_to_file(nomfitxer)
                            # time.sleep(1)
                            with elaudio.container():
                                autoplay_audio(nomfitxer)


else:
    st.write("Afegeix les teves dades i fes click a 'Iniciar Xat'.")
