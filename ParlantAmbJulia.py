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

creaName = "-"
lesinstruccions="Et dius Júlia i ets la millor docent de primària amb molta experiència i coneixement. Ets un assistent experta en aigua, el seu cicle i la seva gestió sostenible. La teva missió és proporcionar informació rigorosa, clara i pràctica sobre la importància de l’aigua, el seu paper en els ecosistemes, els reptes mediambientals que l’afecten i com podem protegir aquest recurs vital. 🔹 Funcions i Objectius de l’Assistent 1️⃣ Explicar el cicle de l’aigua en detall, incloent els processos d’evaporació, condensació, precipitació, infiltració i escorrentia. Diferenciar entre el cicle natural i el cicle de l’aigua en àmbits urbans i agrícoles. 2️⃣ Descriure la importància de l’aigua per a la vida, el clima, els ecosistemes i les societats humanes. 3️⃣ Analitzar problemes ambientals relacionats amb l’aigua, com la contaminació, la sobreexplotació, el canvi climàtic i els conflictes per l’accés a l’aigua. 4️⃣ Fomentar bones pràctiques per a la gestió sostenible de l’aigua, oferint recomanacions per reduir el consum, reutilitzar i protegir fonts d’aigua potable. 5️⃣ Proporcionar activitats pràctiques i experiments per ajudar els usuaris a entendre millor el cicle de l’aigua i el seu ús responsable. Contesta sempre en català sent molt amable i educada. Contesta unicament preguntes relacionades amb els objectius que tens com assistent. MOLT IMPORTANT: - Utilitza NOMÉS la informació disponible en els documents proporcionats. - Si no tens prou informació per respondre una pregunta, digues-ho clarament. - MAI t'inventis informació o facis suposicions no basades en els documents. - Si una pregunta és ambigua o necessites més context, demana clarificació. - Cita específicament d'on treus la informació quan sigui possible. Al final sempre indica que la informació s'ha de validar amb la profesora."
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

st.set_page_config(page_title="Parlant amb Júlia, científica i experta en l'Aigua.", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

#standar alt
l1 = ['xdominguez','mmorel','rlull','ccherrez','gcuanqui','bgutierrez','jmedrano','jpacheco','cmejia']
#standar
l2 = ['lalmanza','hcayo','agarcia','lmorales','dquezada','ssalinas','gsantana']
#standar baix
l3 = ['zasghar','ajaved','hkaur','esingh','ssouza','cuzoho']
#standar baix audio
l4 = ['aenciso','bgomez','rparedes','jperez']
l5 = []
l6 = []
l7 = []
l8 = []

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
    if nom != '' and (nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
        especials = "Contesta sempre amb 3 paràgrafs."
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    else:
        if nom != '':
            st.sidebar.write(":red[Aquest/a usuari/a no existeix]")
        if nom in l2:
            especials3 = "Contesta sempre amb 2 paràgrafs."
        if nom in l3:
            especials6 = "Contesta sempre amb 1 paràgraf."
        if nom in l4:
            especials7 = "Contesta sempre amb 1 paràgraf."
        if nom in l5:
            especials4 = "Contesta sempre amb 1 paràgraf."
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
      especials = "Contesta sempre amb 3 paràgrafs."
  if nom in l2:
      especials3 = "Contesta sempre amb 2 paràgrafs."
  if nom in l3:
      especials6 = "Contesta sempre amb 1 paràgraf."
  if nom in l4:
      especials7 = "Contesta sempre amb 1 pàragraf."
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


st.title("Parlant amb la Júlia")
st.write("Soc inventora, investigadora i experta en l'aigua.")

st.sidebar.button("Sortir del Xat",on_click=enable)

if st.session_state.start_chat:

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if stt_user := speech_to_text(language='es', start_prompt="Fer pregunta amb veu", stop_prompt="Fi de la pregunta",
                                  use_container_width=True, just_once=True, key='STT'):
        prompt = stt_user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    if prompt := st.chat_input("Escriu aquí la teva pregunta"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        if "imatge" in prompt.lower() or "dibuix" in prompt.lower() or "foto" in prompt.lower() or "fotografia" in prompt.lower():
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

                # st.session_state["messages"].append({"role": "assistant", "content": img, "type": "image"})
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response.data[0].url, "type": "image"})
                st.image(response.data[0].url, caption=prompt)

            resinfografria = requests.get(response.data[0].url)
            creaName = str(nom) + "_" + str(time.time()) + "_" + str(2025999999) + ".jpg"
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

            valores = (nom, prompt, creaName, 2025121299, 'PRI2', 'Aigua')
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
                content=prompt + especials + especials3 + especials4 + especials5 + especials6 + especials7
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions=lesinstruccions + especials + especials3 + especials4 + especials5 + especials6 + especials7
            )

            while run.status != 'completed':
                # time.sleep(1)
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
                    if nom in l4:
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos:" + resposta + ".",
                            size="1024x1024",
                            quality="standard",
                            n=1
                        )
                        st.image(response.data[0].url, caption=prompt)
                        resinfografria = requests.get(response.data[0].url)
                        creaName = str(nom) + "_" + str(time.time()) + "_" + str(2025121299) + ".jpg"
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

                    valores = (nom, prompt, message.content[0].text.value, creaName, 2025121299, 'PRI2','Aigua')
                    cur.execute(sql, valores)

                        # Obtiene los resultados de la consulta
                    results_database = cur.fetchall()
                    conn.commit()

                        # Cierra la conexión con la base de datos
                    cur.close()
                    conn.close()

                if nom in l4:
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
    st.write("Afegeix les teves dades y clicka a 'Iniciar Xat'.")