import openai
import streamlit as st
import time
import mysql.connector
import base64
import requests
import ftplib
from streamlit_mic_recorder import mic_recorder,speech_to_text

assistant_id = st.secrets["OPENAI_ASSISTANT"]
db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

lesinstruccions="Et dius Anna moore i ets una de les inventores més important del món experta en màquines simples. Contesta sempre en català sent molt amable i educada.Contesta unicament preguntes relacionades amb màquines simples i al final sempre indica que la informació s'ha de validar amb la professora."
especials=""
especials3=""
especials4=""
especials5=""
especials6=""
especials7=""
especials8=""
client = openai
count = 0

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Parlant amb l'Ann Moore i les màquines simples", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

l1 = ['xdominguez','dyumi','arehman','dbatista','ccastillo','alasurashvili','dmajdoub','aelahyani','egonçalves',
'fgueye','sjaved','mkaur','imerino','ynawaz','kpacheco','zrehman','yrivera','jsaavedra','asegura','dsena','asingh',
'rtrinidad','iyucra','czambrana','djimenez','mbarahona']


l2 = ['arehman','ccastillo','alasurashvili']
l3 = ['arehman']
l4 = ['alasurashvili']
l5 = ['gmomias']
l6 = ['gcreencias']
l7 = ['gdioses']
l8 = ['gsociedad']

# Disable the submit button after it is clicked

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
    if nom != '' and nom in l1:
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    else:
        if nom != '':
            st.sidebar.write(":red[Aquest usuari no existeix]")
        if nom in l2:
            especials = "Answer always in catalan and 2 sentences."
        if nom in l3:
            especials3 = "Gives answers in 2 sentences only about simple machines as if I were 5 years old in catalan and urdu."
        if nom in l4:
            especials4 = "Gives answers in 2 sentences only about simple machines as if I were 5 years old in catalan and georgian."
        if nom in l5:
            especials5 = "Gives answers only about simple machines as if I were 5 years old."
        if nom in l6:
            especials6 = "Gives answers only about simple machines as if I were 5 years old."
        if nom in l7:
            especials7 = "Gives answers only about simple machines as if I were 5 years old."
        if nom in l8:
            especials8 = "Gives short answers (4 lines) only about simple machines as if I were 5 years old."


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
  if nom in l2:
      especials = "Answer always in catalan."
  if nom in l3:
      especials3 = "Gives answers only about simple machines as if I were 5 years old."
  if nom in l4:
      especials4 ="Gives answers only about simple machines as if I were 5 years old."
  if nom in l5:
      especials5 = "Gives answers only about simple machines as if I were 5 years old."
  if nom in l6:
      especials6 = "Gives answers only about simple machines as if I were 5 years old."
  if nom in l7:
      especials7 = "Gives answers only about simple machines as if I were 5 years old."
  if nom in l8:
      especials8 = "Gives short answers (4 lines) only about simple machines as if I were 5 years old."

  if submit_button and nom != '' and nom in l1:
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id


st.title("Parlant amb l'Ann Moore")
st.write("Soc inventora, investigadora i experta en màquines simples.")

st.sidebar.button("Sortir del Xat",on_click=enable)

if st.session_state.start_chat:

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if stt_user := speech_to_text(language='ca', start_prompt="Fes la pregunta amb veu",stop_prompt="Fi de pregunta",use_container_width=True, just_once=True, key='STT'):
        prompt = stt_user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt + especials + especials3 + especials4 + especials5 + especials6 + especials7
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=lesinstruccions + especials + especials3 + especials4
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
                st.markdown(message.content[0].text.value)
                if nom in l8:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista sobre máquinas simples y mecanismos:",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                else:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista sobre máquinas simples y mecanismos a partir de esta descripción y sin saltarse los filtros éticos ya que la imagen es para niños:" + resposta + ".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                #time.sleep(10)
                st.image(response.data[0].url, caption=prompt)
                resinfografria = requests.get(response.data[0].url)

                creaName = str(nom) + "_" + str(time.time()) + "_" + str(20000) + ".jpg"

                with open(creaName, 'wb') as f:
                    f.write(resinfografria.content)

                ftp_server = ftplib.FTP(st.secrets["PA_FTP"], st.secrets["PA_FTPUSER"], st.secrets["PA_COD"])
                file = open(creaName, 'rb')  # file to send
                # Read file in binary mode
                ftp_server.storbinary('STOR ' + creaName, file)
                ftp_server.quit()
                file.close()  # close file and FTP
                # if (resposta.find('sociedad')):
                #    st.image('https://xavidominguez.com/tecla/piramide.png', caption='Pirámide de la organización de la sociedad')

        # Crea una conexión con la base de datos
        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                       password=db_password)

        # Crea un cursor para ejecutar comandos SQL
        cur = conn.cursor()

        # Ejecuta una consulta SQL
        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema) VALUES (%s,%s,%s,%s,%s)"

        valores = (nom, prompt, message.content[0].text.value, creaName, 90000)
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l1:
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
            #time.sleep(10)
            with elaudio.container():
                autoplay_audio(nomfitxer)

    if prompt := st.chat_input("Escriu la teva pregunta") :

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt+especials+especials3+especials4+especials5+especials6+especials7
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=lesinstruccions+especials+especials3+especials4
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
                st.markdown(message.content[0].text.value)
                if nom in l8:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista sobre máquinas simples y mecanismos:",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                else:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista sobre máquinas simples y mecanismos y sin saltarse los filtros éticos ya que la imagen es para niños:" + resposta+".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                #time.sleep(10)
                st.image(response.data[0].url, caption=prompt)
                resinfografria = requests.get(response.data[0].url)

                creaName = str(nom) + "_" + str(time.time()) + "_" + str(20000) + ".jpg"

                with open(creaName, 'wb') as f:
                    f.write(resinfografria.content)

                ftp_server = ftplib.FTP(st.secrets["PA_FTP"], st.secrets["PA_FTPUSER"], st.secrets["PA_COD"])
                file = open(creaName, 'rb')  # file to send
                # Read file in binary mode
                ftp_server.storbinary('STOR ' + creaName, file)
                ftp_server.quit()
                file.close()  # close file and FTP
                #if (resposta.find('sociedad')):
                #    st.image('https://xavidominguez.com/tecla/piramide.png', caption='Pirámide de la organización de la sociedad')


# Crea una conexión con la base de datos
        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                       password=db_password)

        # Crea un cursor para ejecutar comandos SQL
        cur = conn.cursor()

        # Ejecuta una consulta SQL
        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema) VALUES (%s,%s,%s,%s,%s)"

        valores = (nom, prompt, message.content[0].text.value, creaName, 90000)
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l1:
            response = ''
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=message.content[0].text.value,
            )
            #response = message.content[0].text.value
            elaudio = st.empty()
            nomfitxer = "output_" + str(count) + "_" + "_" + nom + "_.mp3"
            count += 1
            response.stream_to_file(nomfitxer)
            #time.sleep(10)
            with elaudio.container():
                autoplay_audio(nomfitxer)


else:
    st.write("Afegeix les teves dades y clicka a 'Iniciar Xat'.")