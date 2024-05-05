import openai
import streamlit as st
import time
import mysql.connector
import base64

assistant_id = st.secrets["OPENAI_ASSISTANT"]
db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

lesinstruccions="Te llamas Salima Ikram y eres la mejor egiptóloga que investiga los secretos del Antiguo Egipto. Contesta siempre en castellano y siendo muy amable y educada. Contesta únicamente preguntas relacionadas con el Antiguo Egipto y al final siempre indica que la información dada se tiene que validar con la profesora."
especials=""
especials3=""
especials4=""
client = openai
count = 0

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="Hablando con Salma y los secretos del Antiguo Egipto", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

l1 = ['xdominguez', 'mcarme','garte','gescritura','gmomias','gcreencias','gdioses','ILAN','ilan','CHLOE','chloe']

l2 = ['ILAN','ilan','garte','gescritura','gmomias','gcreencias','gdioses']
l3 = ['garte']
l4 = ['gescritura']
l5 = ['gmomias']
l6 = ['gcreencias']
l7 = ['gdioses']

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
            st.sidebar.write(":red[Este usuario no existe]")
        if nom in l2:
            especials = "Summarize the answer to 5 lines as if it were being read by an 5 year old child.Give half of the answer in lower case and the other half in capitals."
        if nom in l3:
            especials3 = "Gives answers only about art in Ancient Egypt.Find the answer in the document in the section: 'EL ARTE EN EL ANTIGUO EGIPTO: pintura y escultura.'"
        if nom in l4:
            especials4 = "Gives answers only about writing in Ancient Egypt.Find the answer in the document in the section: 'ESCRITURA EGIPCIA: jeroglíficos y abecedario. '"
        if nom in l5:
            especials5 = "Gives answers only about Mummies in Ancient Egypt.Find the answer in the document in the section:'MOMIAS. Sarcófagos, momias y momificación.'"
        if nom in l6:
            especials6 = "Gives answers only about believes in Ancient Egypt.Find the answer in the document in the section:'CREENCIAS y objetos enterrados en las pirámides'"
        if nom in l7:
            especials7 = "Gives answers only about gods in Ancient Egypt.Find the answer in the document in the section:'MITOLOGÍA, los dioses.'"


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
  nom = st.text_input("Escribe tu identificación 👇",disabled=st.session_state.disabled, key=1)
  submit_button = st.form_submit_button(label="Iniciar Chat",disabled=st.session_state.disabled, on_click=disable)
  if nom in l2:
      especials = "Summarize the answer to 5 lines as if it were being read by an 5 year old child.Give half of the answer in lower case and the other half in capitals."
  if nom in l3:
      especials3 = "Gives answers only about art in Ancient Egypt.Find the answer in the document in the section: 'EL ARTE EN EL ANTIGUO EGIPTO: pintura y escultura.'"
  if nom in l4:
      especials4 = "Gives answers only about writing in Ancient Egypt.Find the answer in the document in the section: 'ESCRITURA EGIPCIA: jeroglíficos y abecedario. '"
  if nom in l5:
      especials5 = "Gives answers only about Mummies in Ancient Egypt.Find the answer in the document in the section:'MOMIAS. Sarcófagos, momias y momificación.'"
  if nom in l6:
      especials6 = "Gives answers only about believes in Ancient Egypt.Find the answer in the document in the section:'CREENCIAS y objetos enterrados en las pirámides'"
  if nom in l7:
      especials7 = "Gives answers only about gods in Ancient Egypt.Find the answer in the document in the section:'MITOLOGÍA, los dioses.'"

  if submit_button and nom != '' and nom in l1:
        st.session_state.disabled = True
        st.session_state.start_chat = True
        st.session_state.disabled = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id


st.title("Hablando con...Salma")
st.write("Soy egiptóloga e investigo los secretos del Antiguo Egipto.")

st.sidebar.button("Salir del Chat",on_click=enable)

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe aquí tu pregunta"):
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
            time.sleep(1)
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
                response = client.images.generate(
                    model="dall-e-3",
                    prompt="Haz una imagen realista que represente este texto:" + resposta,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                st.image(response.data[0].url, caption=prompt)
                #if (resposta.find('sociedad')):
                #    st.image('https://xavidominguez.com/tecla/piramide.png', caption='Pirámide de la organización de la sociedad')


# Crea una conexión con la base de datos
        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                       password=db_password)

        # Crea un cursor para ejecutar comandos SQL
        cur = conn.cursor()

        # Ejecuta una consulta SQL
        sql = "INSERT INTO teclaPREGUNTES (idc,pregunta, resposta,infografia,tema) VALUES (%s,%s,%s,%s,%s)"

        valores = (nom, prompt, message.content[0].text.value, '', 20000)
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
            with elaudio.container():
                autoplay_audio(nomfitxer)

else:
    st.write("Añade tus datos y haz click en 'Iniciar Chat'.")