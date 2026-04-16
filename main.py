import os
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from fetch_api_patient_data import fetch_api_patient_data, find_today_appointment
from img_db_builder import build_embedding_database
from text_recognition import recognizer, text_normalization
from cam_recognition import cam_recognition
from local_db_builder import db_setup, test_connection, get_patients_from_API, populate_db
import cv2


"""
Flusso:
- ricevo audio
- speech-to-text → ottengo nome e cognome
- normalizzo il testo
- cerco nella tua tabella locale
- ottengo uno o più patient_id candidati
- usi il face recognition per scegliere quello giusto
- chiamata API con il patient_id

"""


if __name__ == "__main__":

    db_directory = 'db_imgs'
    destination_directory = 'db_local_embeddings'
    db_file = 'patient_data.db'
    debug_frames = 'debug_frames'
    video_folder = 'test_video'
    audio_pth = 'gabriele_rosati.mp3'

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

    print("Procedo con il riconoscimento vocale ...")
        
    segments = recognizer(audio_pth=audio_pth)
    segments = list(segments) # converto in lista per poter iterare più volte sui segmenti
    print('Ecco il nome del paziente che ho riconosciuto: ')
    print("".join(text_normalization(s.text) for s in segments))

    video_path = os.path.join(video_folder, 'test_video2.mp4')
    cap = cv2.VideoCapture(video_path)
    
    # costruisco il database di embedding a partire dalle immagini dei pazienti solo se non è già stato costruito
    if not os.path.exists(destination_directory):
        build_embedding_database(db_directory, destination_directory) # servirà una logica per aggiornare il database quando ci sono nuovi pazienti o nuove immagini
    patient_id = cam_recognition(destination_directory, cap, debug_frames)
    print(f"Patient ID riconosciuto: {patient_id}")
  
    patient_appointments = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
    today_appointment, timing = find_today_appointment(patient_appointments, patient_id)
