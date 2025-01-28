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

lesinstruccions="Et dius una dona i et dius Felipa . Ets un assistent experta dissenyada per ajudar estudiants de primària a aprendre sobre tres temes principals: 1. **Castells Medievals**: Ets un expert en la història, arquitectura i funció dels castells medievals. Coneixes les característiques arquitectòniques, els elements defensius, la simbologia del poder associada a aquests castells, i les seves funcions en la societat medieval. Pots explicar de manera clara com estaven construïts i la seva relació amb la vida dels nobles i els camperols. 2. **Ús Històric de la Sal**: Ets expert en l'ús de la sal al llarg de la història, especialment en les civilitzacions antigues i medievals. Coneixes el seu paper en la conservació d'aliments, el comerç i la seva importància cultural i simbòlica. Pots explicar els diferents tipus de sal, com la sal marina, les mines de sal, i la relació de la sal amb els salaris. 3. **Comerç i Economia Medievals i Antigues**: Ets expert en l'economia medieval i antiga, amb un enfocament en el comerç de la sal. Coneixes la importància de la sal com a bé comercial, el seu paper en la creació de vies comercials com la Via Salaria romana, i la seva relació amb el concepte de salari. Pots explicar els impactes econòmics i socials de la sal en aquestes èpoques. Només has de respondre a preguntes relacionades amb aquests temes. Si una pregunta no pertany a aquests àmbits, informa a l'usuari que no tens informació sobre aquest tema o que no pots respondre. Mantingues les respostes centrades en la informació dels documents adjunts i en el teu coneixement dins d'aquestes àrees. Quan interactuïs amb els estudiants, utilitza un llenguatge clar i senzill, adequat per a nens de primària. Ofereix respostes concises i fàcils de comprendre, utilitzant exemples visuals quan sigui necessari. Evita utilitzar terminologia massa tècnica i ajuda els estudiants a relacionar els conceptes amb la seva vida quotidiana. Contesta sempre en català i si al prompt de la pregunta especifico un altre idioma contesta en català i la mateixa resposta en l'idioma del prompt. Al final sempre indica que la informació l'has de calidar amb la profesora."
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

st.set_page_config(page_title="Parlant amb Felipa, científica i experta en castells medievals, l'ús històric de la sal i el comerç i l'economia medievals", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

# standar alt
l1 = ['xdominguez', 'raquel','yolanda','econtreras','ccortel','ndimayuga','jescoto','jhossain','jmanalo','trafanan','drodriguez','tsuarez','wjarett','golinares']
# standar
l2 = ['nhabti','aisla','kmuzzamil','azaman']
#standar baix, bangla, imatge,audio
l3 = ['aahmed','suddin']
# standar baix, angles, imatge
l4 = ['kattri','fomabtang','aparajuli']
# standar baix, imatge, audio
l5 = ['jzuluaga']
# standar baix imatge
l6 = ['ctello','cluquingan']
# standar molt baix audio imatge
l7 = ['gmagsombol']
l8 = []
l9 = []

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
    if nom != '' and ( nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
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
            especials6="Contesta sempre amb 1 paràgraf. Repeteix la resposta també amb l'idioma bangla."
        if nom in l4:
            especials7="Contesta sempre amb 1 paràgraf. Repeteix la resposta també amb anglès."
        if nom in l5:
            especials4="Contesta sempre amb 1 paràgraf."
        if nom in l6:
            especials4 = "Contesta sempre amb 1 paràgraf."
        if nom in l7:
            especials5 = "Contesta sempre amb un màxim de 3 frases."

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
      especials6 = "Contesta sempre amb 1 paràgraf. Repeteix la resposta també amb l'idioma bangla."
  if nom in l4:
      especials7 = "Contesta sempre amb 1 paràgraf. Repeteix la resposta també amb anglès."
  if nom in l5:
      especials4 = "Contesta sempre amb 1 paràgraf."
  if nom in l6:
      especials4 = "Contesta sempre amb 1 paràgraf."
  if nom in l7:
      especials5 = "Contesta sempre amb un màxim de 3 frases."

  if submit_button and nom != '' and ( nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id


st.title("Parlant amb...Felipa")
st.write("Soc científica i experta en castells medievals, l'ús històric de la sal i el comerç i l'economia medievals.")

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

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            #content=prompt + especials9
            content=prompt + especials + especials3 + especials4 + especials5 + especials6 + especials7
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=lesinstruccions + especials + especials3 + especials4 + especials5 + especials6 + especials7
            #instructions=lesinstruccions + especials9
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
                if nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7 or nom in l1 or nom in l2:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos:" + resposta + ".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    st.image(response.data[0].url, caption=prompt)
                    resinfografria = requests.get(response.data[0].url)
                    creaName = str(nom) + "_" + str(time.time()) + "_" + str(202500) + ".jpg"
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
        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema,curso,topico) VALUES (%s,%s,%s,%s,%s,%s,%s)"

        valores = (nom, prompt, message.content[0].text.value, creaName, 202500,'PRI2','Castells i Sal')
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l3 or nom in l5 or nom in l7:
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
            #time.sleep(1)
            with elaudio.container():
                autoplay_audio(nomfitxer)

    if prompt := st.chat_input("Escriu aquí la teva pregunta") :

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
                st.markdown(message.content[0].text.value)
                if nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos ya que la imagen es para niños:" + resposta + ".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    st.image(response.data[0].url, caption=prompt)
                    resinfografria = requests.get(response.data[0].url)
                    creaName = str(nom) + "_" + str(time.time()) + "_" + str(202500) + ".jpg"
                    with open(creaName, 'wb') as f:
                        f.write(resinfografria.content)

                    ftp_server = ftplib.FTP(st.secrets["PA_FTP"], st.secrets["PA_FTPUSER"], st.secrets["PA_COD"])
                    file = open(creaName, 'rb')  # file to send
                    # Read file in binary mode
                    ftp_server.storbinary('STOR ' + creaName, file)
                    ftp_server.quit()
                    file.close()  # close file and FTP

                #time.sleep(1)



                #if (resposta.find('sociedad')):
                #    st.image('https://xavidominguez.com/tecla/piramide.png', caption='Pirámide de la organización de la sociedad')


# Crea una conexión con la base de datos
        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                       password=db_password)

        # Crea un cursor para ejecutar comandos SQL
        cur = conn.cursor()

        # Ejecuta una consulta SQL
        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema,curso,topico) VALUES (%s,%s,%s,%s,%s,%s,%s)"

        valores = (nom, prompt, message.content[0].text.value, creaName, 202500,'PRI2','Castells i Sal')
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l3 or nom in l5 or nom in l7:
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
            #time.sleep(1)
            with elaudio.container():
                autoplay_audio(nomfitxer)

else:
    st.write("Afegeix les teves dades i fes click a 'Iniciar Xat'.")
