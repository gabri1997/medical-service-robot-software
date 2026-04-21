from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from fetch_api_patient_data import execute_fetch_and_update
from img_db_builder import build_embedding_database
from text_recognition import execute_text_recognition
from cam_recognition import cam_recognition
from local_db_builder import db_creation
from faster_whisper import WhisperModel
from insightface.app import FaceAnalysis
import cv2
import os


"""
Flow:
    - The patient arrives at the system.
    - Face recognition is attempted.
    - If the face is recognized with high confidence, the corresponding patient_id is retrieved.
    - If the face is not recognized or multiple candidates are detected, the system asks for the patient’s name and surname.
    - The spoken input is transcribed into text.
    - The text is normalized to a consistent format.
    - The system searches the local database using a similarity metric (e.g., Levenshtein distance).
    - One or more candidate patients are retrieved.
    - If necessary, face recognition is used again to disambiguate between candidates.
    - Once the correct patient_id is identified, an API call is made to retrieve the patient’s appointments.

"""


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
    
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    patient_id, best_score = cam_recognition(app, destination_directory, cap, debug_frames)
    cap.release()

    patient_id = None
    # qui sarà da capire che soglia mettere o se il ragionamento è corretto
    if patient_id is None or best_score < 0.5: # se non riesco a riconoscere il paziente con la webcam, o se il punteggio è troppo basso, faccio il fallback con il vocale
        print("Non sono riuscito a riconoscere il paziente, fallback con il vocale ... come ti chiami?")

        model = WhisperModel("small", device="cpu", compute_type="int8")
        audio_path = os.path.join(audio_folder, 'gabriele_rosati.mp3')
        patient_id = execute_text_recognition(audio_path, model, db_file)

        if patient_id == '':
            print("Non sono riuscito a riconoscere il paziente neanche con il vocale, ti prego di avvicinarti alla telecamera per un nuovo tentativo di riconoscimento facciale ...")
       
    if patient_id is not None and patient_id != '':
        print(f"Patient ID riconosciuto: {patient_id}")
        execute_fetch_and_update(patient_id)
  

   
    
    
    
