import cv2
import requests
import os
import numpy as np
from insightface.app import FaceAnalysis
from cam_recognition import cam_recognition
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID



def collect_imgs_from_alfadocs(db_out_dir):
    """
    1 - Prendere le immagini dei pazienti da Alfadocs, per farlo devo capire se è possibile scaricare le immagini del profilo o se è necessario caricarle come documenti associati al paziente, in questo caso dovrei fare una chiamata API per scaricare i documenti associati al paziente e filtrare quelli che sono immagini, poi salvarle in una cartella con il nome del patient_id così da poter costruire il database locale degli embedding a partire da quelle immagini. - In stallo perchè non riesco a recuperare le immagini dei pazienti da Alfadocs, sembra che l'endpoint per le immagini non collezioni le foto profilo, sto cercando di capire se è possibile caricare le foto profilo come documenti associati al paziente così da poterle scaricare tramite API e usarle per il riconoscimento facciale. Se non riesco a recuperare le immagini dei pazienti da Alfadocs, dovrò trovare un'altra soluzione per ottenere le immagini dei pazienti, ad esempio chiedendo ai pazienti di scattare una foto al momento della registrazione o usando un dataset pubblico di volti e associando ogni volto a un patient_id fittizio.
    2 - Organizzare il DB locale usando patient_id come chiave
    3 - Calcolare gli embedding
    """
    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json'
    }
    print("Getting list of documents for each patient...")
    patients_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients"
    patients = requests.get(patients_url, headers=headers)
    print(f"Status: {patients.status_code}")
    patients = patients.json()
    for idx, patient in enumerate(patients['results']):
        patient_id = patients["results"][idx]["id"]
        patient_name = patients["results"][idx]["firstName"]
        patient_surname = patients["results"][idx]["lastName"]
        print(f"Processing patient: {patient_name} {patient_surname} (ID: {patient_id})")
        patient_dir = os.path.join(db_out_dir, str(patient_id))
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir)
        documents_url = f"https://app.alfadocs.com/api/v1/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients/{patient_id}/documents"
        doc_response = requests.get(documents_url, headers=headers)
        if doc_response.status_code != 200:
            print(f"Failed to retrieve documents for patient {patient_name} {patient_surname}.")
            continue
        documents = doc_response.json()
        print(f"Found {len(documents['data'])} documents for patient {patient_name} {patient_surname}.")
        for i in range(len(documents['data'])):
            doc_id = documents['data'][i][i]['id']
            doc_name = documents['data'][i][i]['name']
            doc_down_lin = documents['data'][i][i]['downloadUrl']
            if doc_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"Downloading document {doc_name} for patient {patient_name} {patient_surname}...")
                doc_url = doc_down_lin
                doc_response = requests.get(doc_url, headers=headers)
                print(doc_response.status_code)
                print(doc_response.headers.get("Content-Type"))
                print(len(doc_response.content))
                if doc_response.status_code == 200:
                    img_path = os.path.join(patient_dir, doc_name)
                    with open(img_path, 'wb') as f:
                        f.write(doc_response.content)
                        print(img_path)
                        print(os.path.exists(img_path))
                        print(os.path.getsize(img_path))
                    print(f"Saved document {doc_name} for patient {patient_name} {patient_surname}.")
                else:
                    print(f"Failed to download document {doc_name} for patient {patient_name} {patient_surname}.")
            
    

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    db_out_dir = os.path.join(
        BASE_DIR,
        "db_imgs"
    )
  
    if not os.path.exists(db_out_dir):
        os.makedirs(db_out_dir)
    collect_imgs_from_alfadocs(db_out_dir)