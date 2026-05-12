from fetch_api_patient_data import execute_fetch_and_update
from img_db_builder import build_embedding_database
from text_recognition import execute_text_recognition
from cam_recognition import cam_recognition
from local_db_builder import db_creation
from faster_whisper import WhisperModel
from insightface.app import FaceAnalysis
import cv2
import os
from notifier import notify_event
from config import FACE_RECOGNITION_THRESHOLD

"""
Flow:
    - The patient arrives at the system.
    - Face recognition is attempted.
    - If the face is recognized with high confidence (>FACE_RECOGNITION_THRESHOLD), the corresponding patient_id is retrieved.
    - If the face is not recognized (or the confidence score is too low), the system asks for the patient’s name and surname.
    - The spoken input is transcribed into text.
    - The text is normalized to a consistent format.
    - The system searches the local database using a similarity metric (e.g., Levenshtein distance).
    - Once the correct patient_id is identified, an API call is made to retrieve the patient’s appointments.
"""

# TODO:
# - capire come settare i vari stati degli appuntamenti a seconda del momento in cui arriva il paziente
# - se ci sono più appuntamenti in un giorno ci si riferisce al più vicino all'orario di arrivo del paziente
# - capire se va bene usare la levenshtein distance come metrica di similarità testuale
# - capire se serve disambiguare i pazienti se fallisce il riconoscimento facciale e quello vocale da piu risultati

if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    db_directory = os.path.join(BASE_DIR, 'db_imgs')
    destination_directory = os.path.join(BASE_DIR, 'db_local_embeddings')
    db_file = os.path.join(BASE_DIR, 'patient_data.db')
    debug_frames = os.path.join(BASE_DIR, 'debug_frames')
    video_folder = os.path.join(BASE_DIR, 'test_video')
    audio_folder = os.path.join(BASE_DIR, 'audio')

    print("Inizio il processo di riconoscimento del paziente ...")

    if not os.path.exists(db_file):
        db_creation(db_file)
    else:
        print("Database già esistente, procedo con il riconoscimento del paziente ...")

    
    video_path = os.path.join(video_folder, 'test_video2.mp4')
    cap = cv2.VideoCapture(video_path)
    
    # costruisco il database di embedding a partire dalle immagini dei pazienti solo se non è già stato costruito
    if not os.path.exists(destination_directory):
        build_embedding_database(db_directory, destination_directory) # servirà una logica per aggiornare il database quando ci sono nuovi pazienti o nuove immagini
    
    # Stop policy webcam: massimo frame, campionamento e uscita anticipata su score alto.
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    patient_id, best_score = cam_recognition(
        app,
        destination_directory,
        cap,
        debug_frames,
        max_frames=120,
        process_every_n_frames=3,
        early_stop_score=0.72,
    )
    cap.release()

    # patient_id = None # per debuggare la parte di text recognition, forzo il riconoscimento facciale a non funzionare, così posso testare la parte di riconoscimento vocale e di similarità testuale
    # qui sarà da capire che soglia mettere o se il ragionamento è corretto
    if patient_id is None or best_score is None or best_score < FACE_RECOGNITION_THRESHOLD: # se non riesco a riconoscere il paziente con la webcam, o se il punteggio è troppo basso, faccio il fallback con il vocale
        print("Non sono riuscito a riconoscere il paziente, fallback con il vocale ... come ti chiami?")

        model = WhisperModel("small", device="cpu", compute_type="int8")
        audio_path = os.path.join(audio_folder, 'gabriele_rosati.mp3')
        patient_id = execute_text_recognition(audio_path, model, db_file)

        if patient_id is None:
            print("Non sono riuscito a riconoscere il paziente neanche con il vocale, ti prego di avvicinarti alla telecamera per un nuovo tentativo di riconoscimento facciale ...")
            notify_event("Patient_not_recognized")

    if patient_id is not None:
        print(f"Patient ID riconosciuto: {patient_id}")
        execute_fetch_and_update(patient_id)




    
    
    
