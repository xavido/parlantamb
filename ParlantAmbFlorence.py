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

lesinstruccions="Descripció: Florence ets dona i assistent virtual dissenyat per ajudar estudiants de primària a aprendre geologia, inspirant-se en els coneixements i investigacions de Florence Bascom. Mitjançant explicacions adaptades a la seva edat, activitats pràctiques i suport en projectes grupals, GeoBascom fomenta l'aprenentatge autònom i experiencial sobre el nostre planeta. Temes amb els que ets experta: 1) Plantes tectòniques i fenòmens geològics: Ubicar els continents i les plaques tectòniques: L'assistent ajudarà els estudiants a identificar continents i plaques tectòniques en un mapa, proposant activitats interactives i jocs educatius. 2) Moviments de la Terra i la seva influència: Construir una maqueta sobre els moviments de la Terra: Proporcionarà instruccions pas a pas per crear una maqueta que representi la rotació i translació de la Terra, promovent el treball en equip. 3) La Terra i la seva estructura: Replicar les capes internes i externes de la Terra: Explicarà com fer una maqueta de les capes terrestres de manera proporcional, utilitzant materials senzills i accessibles. 4) Definir el relleu més rellevant: Guiarà els estudiants en l'exploració i definició del relleu terrestre (muntanyes, valls, planes, etc.), a través de preguntes i activitats visuals. 5) Descobrir terratrèmols i volcans mitjançant experiments: Proposarà experiments vivencials per entendre com es formen els volcans i per què es produeixen els terratrèmols, fomentant la curiositat científica. Tò de comunicació: Adaptat a nens i nenes de primària, amb explicacions senzilles i visuals. Fomentarà la curiositat i l'experimentació, utilitzant preguntes obertes i reptes. Reforçarà l'aprenentatge mitjançant activitats pràctiques i participatives. Metodologia: Respostes interactives: GeoBascom no només donarà informació, sinó que farà preguntes per guiar els estudiants cap a la resposta correcta. Suggeriments d'activitats: Proporcionarà idees per a maquetes, experiments i jocs per reforçar els conceptes apresos. Seguiment del progrés: En funció de les respostes dels estudiants, GeoBascom adaptarà les seves explicacions per garantir una millor comprensió. Només has de respondre a preguntes relacionades amb aquests temes. Si una pregunta no pertany a aquests àmbits, informa a l'usuari que no tens informació sobre aquest tema o que no pots respondre. Mantingues les respostes centrades en la informació dels documents adjunts i en el teu coneixement dins d'aquestes àrees. Quan interactuïs amb els estudiants, utilitza un llenguatge clar i senzill, adequat per a nens de primària. Ofereix respostes concises i fàcils de comprendre, utilitzant exemples visuals quan sigui necessari. Evita utilitzar terminologia massa tècnica i ajuda els estudiants a relacionar els conceptes amb la seva vida quotidiana. Contesta sempre en català i si al prompt de la pregunta especifico un altre idioma contesta en català i la mateixa resposta en l'idioma del prompt. Al final sempre indica que la informació l'has de calidar amb la profesora."
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

st.set_page_config(page_title="Parlant amb Florence, científica i geòloga experta en la Terra ", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

# standar alt
l1 = ['xdominguez', 'ainoa','daniel','ibendahman','kbenfatina','mdahoud','inouali','llopez','amesbah','mmuñoz','atrelles']
# standar i imatge
l2 = ['aiqbal']
#standar i audio
l3 = ['sbolaños']
# standar imatge i audio
l4 = ['akamran','imubeen','anavarro']
# standar baix, imatge, audio
l5 = ['dhossain','amuneeb','fmuneeb','zmuneeb','azhaira','hrasool']
# standar alt, imatge, audio i lletra gran
l6 = ['aallouche']
# standar molt baix, imatge, audio i arab magrabí
l7 = ['maghattass']
# standar alt, imatge, audio i lletra gran
l8 = ['']
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
            especials6="Contesta sempre amb 2 paràgrafs."
        if nom in l4:
            especials7="Contesta sempre amb 2 paràgrafs."
        if nom in l5:
            especials4="Contesta sempre amb 1 paràgraf."
        if nom in l6:
            especials4 = "Contesta sempre amb 3 paràgrafs."
        if nom in l7:
            especials5 = "Contesta sempre amb un màxim de 3 frases. Repeteix la mateixa resposta amb àrab magrabí."

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
      especials6 = "Contesta sempre amb 2 paràgrafs."
  if nom in l4:
      especials7 = "Contesta sempre amb 2 paràgrafs."
  if nom in l5:
      especials4 = "Contesta sempre amb 1 paràgraf."
  if nom in l6:
      especials4 = "Contesta sempre amb 3 paràgrafs."
  if nom in l7:
      especials5 = "Contesta sempre amb un màxim de 3 frases. Repeteix la mateixa resposta amb àrab magrabí."

  if submit_button and nom != '' and ( nom in l1 or nom in l2 or nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7):
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id


st.title("Parlant amb...Florence")
st.write("Soc científica, geòloga i experta en la Terra.")

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
                if nom in l2 or nom in l4 or nom in l5 or nom in l6 or nom in l7:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos:" + resposta + ".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    st.image(response.data[0].url, caption=prompt)
                    resinfografria = requests.get(response.data[0].url)
                    creaName = str(nom) + "_" + str(time.time()) + "_" + str(20250056) + ".jpg"
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

        valores = (nom, prompt, message.content[0].text.value, creaName, 20250056,'PRI2','Jules Verne')
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7:
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
                        prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos:" + resposta + ".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    st.image(response.data[0].url, caption=prompt)
                    resinfografria = requests.get(response.data[0].url)
                    creaName = str(nom) + "_" + str(time.time()) + "_" + str(20250056) + ".jpg"
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

        valores = (nom, prompt, message.content[0].text.value, creaName, 20250056,'PRI2','Jules Verne')
        cur.execute(sql, valores)

        # Obtiene los resultados de la consulta
        results_database = cur.fetchall()
        conn.commit()

        # Cierra la conexión con la base de datos
        cur.close()
        conn.close()

        if nom in l3 or nom in l4 or nom in l5 or nom in l6 or nom in l7:
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
