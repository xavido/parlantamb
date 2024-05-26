import openai
import streamlit as st
import time
import mysql.connector
import base64
import requests
import ftplib
import numpy as np
from streamlit_webrtc import WebRtcMode, webrtc_streamer
# from streamlit_webrtc import VideoTransformerBase, VideoTransformerContext

from pydub import AudioSegment
import queue, pydub, tempfile,  os

assistant_id = st.secrets["OPENAI_ASSISTANT"]
db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

lesinstruccions="Te llamas Salima Ikram y eres la mejor egiptóloga que investiga los secretos del Antiguo Egipto. Contesta siempre en castellano y siendo muy amable y educada.Contesta únicamente preguntas relacionadas con el Antiguo Egipto y al final siempre indica que la información dada se tiene que validar con la profesora."
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

st.set_page_config(page_title="Hablando con Salma y los secretos del Antiguo Egipto", page_icon=":speech_balloon:")

openai.api_key = st.secrets["auto_pau"]

l1 = ['xdominguez', 'mcarme','garte','gescritura','gmomias','gcreencias','gdioses','ILAN','ilan','CHLOE','chloe','gsociedad']

l2 = ['ILAN','ilan','garte','gescritura','gmomias','gcreencias','gdioses','gsociedad']
l3 = ['garte']
l4 = ['gescritura']
l5 = ['gmomias']
l6 = ['gcreencias']
l7 = ['gdioses']
l8 = ['gsociedad']


# functions

ef
save_audio(audio_segment: AudioSegment, base_filename: str) -> None:
"""
Save an audio segment to a .wav file.
Args:
    audio_segment (AudioSegment): The audio segment to be saved.
    base_filename (str): The base filename to use for the saved .wav file.
"""
filename = f"{base_filename}_{int(time.time())}.wav"
audio_segment.export(filename, format="wav")


def transcribe(audio_segment: AudioSegment, debug: bool = False) -> str:
    """
    Transcribe an audio segment using OpenAI's Whisper ASR system.
    Args:
        audio_segment (AudioSegment): The audio segment to transcribe.
        debug (bool): If True, save the audio segment for debugging purposes.
    Returns:
        str: The transcribed text.
    """
    if debug:
        save_audio(audio_segment, "debug_audio")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        audio_segment.export(tmpfile.name, format="wav")
        answer = openai.Audio.transcribe(
            "whisper-1",
            tmpfile,
            temperature=0.2,
            prompt="",
        )["text"]
        tmpfile.close()
        os.remove(tmpfile.name)
        return answer


def frame_energy(frame):
    """
    Compute the energy of an audio frame.
    Args:
        frame (VideoTransformerBase.Frame): The audio frame to compute the energy of.
    Returns:
        float: The energy of the frame.
    """
    samples = np.frombuffer(frame.to_ndarray().tobytes(), dtype=np.int16)
    return np.sqrt(np.mean(samples ** 2))


def process_audio_frames(audio_frames, sound_chunk, silence_frames, energy_threshold):
    """
    Process a list of audio frames.
    Args:
        audio_frames (list[VideoTransformerBase.Frame]): The list of audio frames to process.
        sound_chunk (AudioSegment): The current sound chunk.
        silence_frames (int): The current number of silence frames.
        energy_threshold (int): The energy threshold to use for silence detection.
    Returns:
        tuple[AudioSegment, int]: The updated sound chunk and number of silence frames.
    """
    for audio_frame in audio_frames:
        sound_chunk = add_frame_to_chunk(audio_frame, sound_chunk)

        energy = frame_energy(audio_frame)
        if energy < energy_threshold:
            silence_frames += 1
        else:
            silence_frames = 0

    return sound_chunk, silence_frames


def add_frame_to_chunk(audio_frame, sound_chunk):
    """
    Add an audio frame to a sound chunk.
    Args:
        audio_frame (VideoTransformerBase.Frame): The audio frame to add.
        sound_chunk (AudioSegment): The current sound chunk.
    Returns:
        AudioSegment: The updated sound chunk.
    """
    sound = pydub.AudioSegment(
        data=audio_frame.to_ndarray().tobytes(),
        sample_width=audio_frame.format.bytes,
        frame_rate=audio_frame.sample_rate,
        channels=len(audio_frame.layout.channels),
    )
    sound_chunk += sound
    return sound_chunk


def handle_silence(sound_chunk, silence_frames, silence_frames_threshold, text_output):
    """
    Handle silence in the audio stream.
    Args:
        sound_chunk (AudioSegment): The current sound chunk.
        silence_frames (int): The current number of silence frames.
        silence_frames_threshold (int): The silence frames threshold.
        text_output (st.empty): The Streamlit text output object.
    Returns:
        tuple[AudioSegment, int]: The updated sound chunk and number of silence frames.
    """
    if silence_frames >= silence_frames_threshold:
        if len(sound_chunk) > 0:
            text = transcribe(sound_chunk)
            text_output.write(text)
            sound_chunk = pydub.AudioSegment.empty()
            silence_frames = 0

    return sound_chunk, silence_frames


def handle_queue_empty(sound_chunk, text_output):
    """
    Handle the case where the audio frame queue is empty.
    Args:
        sound_chunk (AudioSegment): The current sound chunk.
        text_output (st.empty): The Streamlit text output object.
    Returns:
        AudioSegment: The updated sound chunk.
    """
    if len(sound_chunk) > 0:
        text = transcribe(sound_chunk)
        text_output.write(text)
        sound_chunk = pydub.AudioSegment.empty()

    return sound_chunk


def app_sst(
        status_indicator,
        text_output,
        timeout=3,
        energy_threshold=2000,
        silence_frames_threshold=100
):
    """
    The main application function for real-time speech-to-text.
    This function creates a WebRTC streamer, starts receiving audio data, processes the audio frames,
    and transcribes the audio into text when there is silence longer than a certain threshold.
    Args:
        status_indicator: A Streamlit object for showing the status (running or stopping).
        text_output: A Streamlit object for showing the transcribed text.
        timeout (int, optional): Timeout for getting frames from the audio receiver. Default is 3 seconds.
        energy_threshold (int, optional): The energy threshold below which a frame is considered silence. Default is 2000.
        silence_frames_threshold (int, optional): The number of consecutive silence frames to trigger transcription. Default is 100 frames.
    """
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    sound_chunk = pydub.AudioSegment.empty()
    silence_frames = 0

    while True:
        if webrtc_ctx.audio_receiver:
            status_indicator.write("Running. Say something!")

            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=timeout)
            except queue.Empty:
                status_indicator.write("No frame arrived.")
                sound_chunk = handle_queue_empty(sound_chunk, text_output)
                continue

            sound_chunk, silence_frames = process_audio_frames(audio_frames, sound_chunk, silence_frames,
                                                               energy_threshold)
            sound_chunk, silence_frames = handle_silence(sound_chunk, silence_frames, silence_frames_threshold,
                                                         text_output)
        else:
            status_indicator.write("Stopping.")
            if len(sound_chunk) > 0:
                text = transcribe(sound_chunk.raw_data)
                text_output.write(text)
            break


# endfunctions
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
            especials = "Answer always in spanish."
        if nom in l3:
            especials3 = "Gives answers only about art in Ancient Egypt.Find the answer especially in the context of ART IN ANCIENT EGYPT: painting and sculpture."
        if nom in l4:
            especials4 = "Gives answers only about writing in Ancient Egypt.Find the answer especially in the context of  EGYPTIAN WRITING: hieroglyphs and alphabet."
        if nom in l5:
            especials5 = "Gives answers only about Mummies in Ancient Egypt.Find the answer especially in the context of  Sarcophagi, mummies and mummification."
        if nom in l6:
            especials6 = "Gives answers only about believes in Ancient Egypt.Find the answer especially in the context of BELIEFS and objects buried in the pyramids."
        if nom in l7:
            especials7 = "Gives answers only about gods in Ancient Egypt.Find the answer especially in the context of MYTHOLOGY, the gods."
        if nom in l8:
            especials8 = "Gives short answers (4 lines) only about society in Ancient Egypt.Find the answer especially in the context of organization of society in Ancient Egypt"


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
      especials = "Answer always in spanish."
  if nom in l3:
      especials3 = "Gives answers only about art in Ancient Egypt.Find the answer especially in the context of ART IN ANCIENT EGYPT: painting and sculpture."
  if nom in l4:
      especials4 = "Gives answers only about writing in Ancient Egypt.Find the answer especially in the context of  EGYPTIAN WRITING: hieroglyphs and alphabet."
  if nom in l5:
      especials5 = "Gives answers only about Mummies in Ancient Egypt.Find the answer especially in the context of  Sarcophagi, mummies and mummification."
  if nom in l6:
      especials6 = "Gives answers only about believes in Ancient Egypt.Find the answer especially in the context of BELIEFS and objects buried in the pyramids."
  if nom in l7:
      especials7 = "Gives answers only about gods in Ancient Egypt.Find the answer especially in the context of MYTHOLOGY, the gods."
  if nom in l8:
      especials8 = "Gives short answers (4 lines) only about society in Ancient Egypt.Find the answer especially in the context of organization of society in Ancient Egypt"

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
                if nom in l8:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista sobre la estructura de la sociedad y las personas en el Antiguo Egipto:",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                else:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt="Haz una imagen realista a partir de esta descripción y sin saltarse los filtros éticos ya que la imagen es para niños:" + resposta+".",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                time.sleep(10)
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

        valores = (nom, prompt, message.content[0].text.value, creaName, 20000)
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
            time.sleep(10)
            with elaudio.container():
                autoplay_audio(nomfitxer)

else:
    st.write("Añade tus datos y haz click en 'Iniciar Chat'.")