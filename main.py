from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from fetch_api_patient_data import fetch_api_patient_data, find_today_appointment
from img_db_builder import build_embedding_database
from text_recognition import recognizer, text_normalization
from cam_recognition import cam_recognition
from local_db_builder import db_setup, get_patients_from_API, populate_db
from faster_whisper import WhisperModel
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
    print("Creo il db locale se non esiste già ...")

    if not os.path.exists(db_file):
        print("Database non trovato, procedo con la creazione del database ...")
        connection, cursor = db_setup()
        patients_list = get_patients_from_API(API_KEY, PRACTICE_ID, ARCHIVE_ID)
        populate_db(connection, cursor, patients_list)
        cursor.close()
        connection.close()
    else:
        print("Database già esistente, procedo con il riconoscimento del paziente ...")

    
    video_path = os.path.join(video_folder, 'test_video2.mp4')
    cap = cv2.VideoCapture(video_path)
    
    # costruisco il database di embedding a partire dalle immagini dei pazienti solo se non è già stato costruito
    if not os.path.exists(destination_directory):
        build_embedding_database(db_directory, destination_directory) # servirà una logica per aggiornare il database quando ci sono nuovi pazienti o nuove immagini
    
    patient_id = cam_recognition(destination_directory, cap, debug_frames)
    cap.release()
    if patient_id is None:
        print("Non sono riuscito a riconoscere il paziente, fallback con il vocale ...")
        audio_pth = os.path.join(audio_folder, 'gabriele_rosati.mp3')
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments = recognizer(audio_pth=audio_pth, model=model)
        segments = list(segments) # converto in lista per poter iterare più volte sui segmenti
        full_text = " ".join(s.text for s in segments)
        normalized_name = text_normalization(full_text) # prima concateno e poi normalizzo
        print(f"Ecco il nome del paziente che ho riconosciuto: {normalized_name}")
    else:
        print(f"Patient ID riconosciuto: {patient_id}")
        patient_appointments = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
        today_appointment, timing = find_today_appointment(patient_appointments, patient_id)
        print(f"Appuntamento di oggi per il paziente {patient_id}: {today_appointment} alle {timing}")

   
    
    
    
