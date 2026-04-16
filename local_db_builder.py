import os
import sqlite3
import requests
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from text_recognition import text_normalization
from datetime import datetime, timezone



def db_setup():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "patient_data.db")
    connection = sqlite3.connect(db_path) # prima creo una connessione con il db
    cursor = connection.cursor() # questo mi serve per fare il fetch dei risultati dalle queries
    cursor.execute("CREATE TABLE IF NOT EXISTS patients(patient_id TEXT PRIMARY KEY, name TEXT NOT NULL, surname TEXT NOT NULL, full_normalized_name TEXT, img_folder TEXT, last_sync TEXT)") # creo la tabella se non esiste già
    connection.commit()
    return connection, cursor

def test_connection():
    connection, cursor = db_setup()
    cursor.execute("INSERT OR REPLACE INTO patients (patient_id, name, surname, full_normalized_name, img_folder, last_sync) VALUES (?, ?, ?, ?, ?, ?)", ("101884589", "Gabriele", "Rosati", "gabriele rosati", "db_imgs/gabriele_rosati", None)) # inserisco un paziente di test
    cursor.execute("SELECT * FROM patients") # faccio una query per vedere se ci sono già dati nella tabella
    rows = cursor.fetchall() # prendo i risultati della query, tutte le righe
    for row in rows:
        print(row) # stampo i risultati della query, ogni riga è una tupla con i dati di un paziente
    connection.close() # chiudo la connessione al db

def get_patients_from_API(API_KEY, PRACTICE_ID, ARCHIVE_ID): # questa funzione serve per ottenere i dati dei pazienti da un'API, la implemento dopo
    
    patients_list = []
    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json'
    }
    print("Testing: List all patients...")
    patients_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients"
    response = requests.get(patients_url, headers=headers) # quando fai la richiesta GET ti serve l'URL e la chiave API
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print("Failed to retrieve patients.")
        return patients_list
    
    patients = response.json() # se la richiesta va a buon fine, prendo i dati dei pazienti in formato JSON
    print(f"Found {len(patients['results'])} patients.")

    for idx, _ in enumerate(patients['results']): # itero sui pazienti, ogni paziente è un dizionario con i suoi dati
        patient_id = patients["results"][idx]["id"]
        patient_name = patients["results"][idx]["firstName"]
        patient_surname = patients["results"][idx]["lastName"]
        print(f"Processing patient: {patient_name} {patient_surname} (ID: {patient_id})")
        paziente = {"patient_id" : patient_id, "patient_name" : patient_name, "patient_surname": patient_surname}
        patients_list.append(paziente)

    return patients_list

def populate_db(connection ,cursor, patients_list):
    #[{'patient_id': 101884589, 'patient_name': 'GABRIELE', 'patient_surname': 'ROSATI'}, {'patient_id': 101950247, 'patient_name': 'Ettore', 'patient_surname': 'Candeloro'}, {'patient_id': 103321161, 'patient_name': 'Mario', 'patient_surname': 'Rossi'}]
    print("Devo inseriere il seguente numero di pazienti nel database locale: {}".format(len(patients_list)))
    for patient in patients_list:
        patient_id = patient["patient_id"]
        patient_name = patient["patient_name"]
        patient_surname = patient["patient_surname"]
        full_normalized_name = text_normalization(patient_name + " " + patient_surname)
        img_folder = f"db_imgs/{patient_id}"
        last_sync = datetime.now(timezone.utc).isoformat()
        print(f"Inserisco il paziente {patient_name} {patient_surname} con ID {patient_id} nel database locale ...")
        cursor.execute("INSERT OR REPLACE INTO patients (patient_id, name, surname, full_normalized_name, img_folder, last_sync) VALUES (?, ?, ?, ?, ?, ?)", (patient_id, patient_name, patient_surname, full_normalized_name, img_folder, last_sync))
    
    connection.commit() # salvo le modifiche al db
   
    
    print("Database popolato con successo!")

   

if __name__ == '__main__':
    connection , cursor = db_setup()
    # test_connection() # questa funzione serve solo per testare se la connessione al db funziona e se riesco a creare la tabella e inserire dati, la commento dopo averla testata
    populate_db(connection, cursor, get_patients_from_API(API_KEY, PRACTICE_ID, ARCHIVE_ID)) # questa funzione serve per popolare il db con i dati dei pazienti ottenuti dall'API, la implemento dopo
    connection.close()
    print("Processo completato, database chiuso.")