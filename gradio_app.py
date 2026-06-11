import gradio
from fetch_api_patient_data import execute_fetch_and_update
from img_db_builder import build_embedding_database
from collect_imgs_from_alfadocs import collect_imgs_from_alfadocs
from text_recognition import execute_text_recognition
from llm_state.agent_state import AgentState
from cam_recognition import cam_recognition, identify_from_image
from local_db_builder import db_creation
from faster_whisper import WhisperModel
from insightface.app import FaceAnalysis
import cv2
import os
import numpy as np
from notifier import notify_event
from config import FACE_RECOGNITION_THRESHOLD

patient_id = None

def initialize_system():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_directory = os.path.join(BASE_DIR, 'db_imgs')
    destination_directory = os.path.join(BASE_DIR, 'db_local_embeddings')
    db_file = os.path.join(BASE_DIR, 'patient_data.db')

    if not os.path.exists(db_file):
        db_creation(db_file)
    else:
        print("Database già esistente, procedo con il riconoscimento del paziente ...")
    
    # Aggiungere le immagini dei pazienti tramite Alfadocs e poi fare la chiamata API su Documents per recupere il documento immagine allegato al paziente (per ognuno)
    if not os.path.exists(destination_directory):
        print("Costruisco il database di embedding a partire dalle immagini dei pazienti ...")
        collect_imgs_from_alfadocs(db_directory)
        build_embedding_database(db_directory, destination_directory) # servirà una logica per aggiornare il database quando ci sono nuovi pazienti o nuove immagini
    else:
        print("Database di embedding già esistente, procedo con il riconoscimento del paziente ...")

    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    app.prepare(ctx_id=0, det_size=(640, 640))
    
    DB = np.load(os.path.join(destination_directory, 'db_embeddings.npz'))

    return app, DB

def identify_from_webcam(image):
    print(type(image))
    if image is not None:
        print(image.shape)
    global patient_id
    result = identify_from_image(face_app,DB,image)
    patient_id = result["patient_id"]
    return result


def check_in():
    global patient_id
    if patient_id is None:
        return "No patient identified yet. Please start the identification process first."
    result = execute_fetch_and_update(patient_id)
    if result["success"]:
        # qui devo ritornarlo formattato cosi visto che il backend ritorna un dizionario
        return (
            f"Check-in completed.\n"
            f"Status: {result['data']['new_status']}\n"
            f"Timing: {result['data']['timing']}"
        )

    return f"Error: {result['event']}"

def reset():
    global patient_id
    patient_id = None
    return "Session reset."

face_app, DB = initialize_system()

with gradio.Blocks(title="Sistema di Accettazione Pazienti") as demo:

    gradio.Markdown("""
    # 🏥 Sistema di Accettazione Pazienti

    ## Istruzioni

    ### 1️⃣ Attivare la fotocamera
    Premere **Use Webcam** sotto l'anteprima video.

    ### 2️⃣ Scattare una foto
    Premere **Take Photo**.

    ### 3️⃣ Riconoscere il paziente
    Premere **Riconosci Paziente**.

    ### 4️⃣ Effettuare il check-in
    Se il riconoscimento è andato a buon fine, premere **Esegui Check-in**.
""")

    webcam = gradio.Image(
        sources=["webcam"],
        type="numpy",
        label="📷 Fotocamera Paziente",
        height=500
    )

    risultato_riconoscimento = gradio.JSON(
        label="Risultato riconoscimento"
    )

    stato_operazione = gradio.Textbox(
        label="Stato operazione"
    )

    riconosci_btn = gradio.Button(
        "Riconosci Paziente",
        variant="primary",
        size="lg"
    )

    checkin_btn = gradio.Button(
        "Esegui Check-in",
        variant="primary"
    )

    reset_btn = gradio.Button(
        "Nuova Sessione"
    )

    riconosci_btn.click(
        identify_from_webcam,
        inputs=webcam,
        outputs=risultato_riconoscimento
    )

    checkin_btn.click(
        check_in,
        outputs=stato_operazione
    )

    reset_btn.click(
        reset,
        outputs=stato_operazione
    )


demo.launch(share=True)