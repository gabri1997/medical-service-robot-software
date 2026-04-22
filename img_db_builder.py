import os
import cv2
import requests
import numpy as np
from insightface.app import FaceAnalysis
from cam_recognition import cam_recognition
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID

# questa cosa non si può fare perchè l'endpoint non colleziona le immagini di profilo
def collect_imgs_from_alfadocs(db_directory):
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)

    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json'
    }
  
    
    print("Testing: List all patients...")
    patients_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients"
    response = requests.get(patients_url, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print("Failed to retrieve patients.")
        return
    
    patients = response.json()
    print(f"Found {len(patients['results'])} patients.")
    for idx, patient in enumerate(patients['results']):
        patient_id = patients["results"][idx]["id"]
        # 'results': [{'id': 101884589, 'firstName': 'GABRIELE', 'lastName': 'ROSATI', 'email': 'gabrielerosati97@gmail.com', 'emailEnabled': False, 'emailValid': True, 'phoneNumbers': [...], 'gender': None, 'street': None, 'city': None, 'postcode': None, 'province': '', 'dateBirth': None, 'placeOfBirth': None, 'italianFiscalCode': None, 'job': None, 'yearlyNumberingYear': None, 'yearlyNumberingNumber': None, 'defaultDiscount': None, ...}, {'id': 101950247, 'firstName': 'Ettore', 'lastName': 'Candeloro', 'email': 'ettorecandeloro@gmail.com', 'emailEnabled': False, 'emailValid': True, 'phoneNumbers': [...], 'gender': None, 'street': None, 'city': None, 'postcode': None, 'province': '', 'dateBirth': None, 'placeOfBirth': None, 'italianFiscalCode': None, 'job': None, 'yearlyNumberingYear': None, 'yearlyNumberingNumber': None, 'defaultDiscount': None, ...}]
        patient_name = patients["results"][idx]["firstName"]
        patient_surname = patients["results"][idx]["lastName"]
        print(f"Processing patient: {patient_name} {patient_surname} (ID: {patient_id})")
        # genero la cartella chamata con l'id del paziente
        patient_dir = os.path.join(db_directory, str(patient_id))
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir)
        # prendo tutte le immagini del paziente, spoiler non ce ne sono anche se carico la foto profilo
        images_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients/{patient_id}/images"
        response = requests.get(images_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve images for patient {patient_name} {patient_surname}.")
            continue
        images = response.json()
        print(f"Found {len(images)} images for patient {patient_name} {patient_surname}.")
        # salvo le immagini nella cartella 
        for img in images:
            img_id = img["results"][1]["id"]
            img_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients/{patient_id}/images/{img_id}/download"
            img_response = requests.get(img_url, headers=headers)
            if img_response.status_code == 200:
                img_path = os.path.join(patient_dir, f"{img_id}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"Saved image {img_id} for patient {patient_name} {patient_surname}.")
            else:
                print(f"Failed to download image {img_id} for patient {patient_name} {patient_surname}.")

    

def build_embedding_database(db_directory, destination_directory):
    
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    # la det_size è importante per la qualità dell'embedding, ma aumenta il tempo di elaborazione. 640x640 è un buon compromesso.
    app.prepare(ctx_id=0, det_size=(640, 640))

    embeddings = []
    labels = []

    for human_dir in os.listdir(db_directory):
        human_path = os.path.join(db_directory, human_dir)
        if os.path.isdir(human_path):
            for img_name in os.listdir(human_path):
                img_path = os.path.join(human_path, img_name)
                img = cv2.imread(img_path)

                if img is None:
                    print(f"Could not read image: {img_path}")
                    continue

                faces = app.get(img)
                if len(faces) == 0:
                    print(f"No face detected in image: {img_path}")
                    continue

                face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
                emb = face.embedding.astype(np.float32)

                emb = emb / np.linalg.norm(emb)
                embeddings.append(emb)
                labels.append(human_dir)

                print(f"[OK] ---> Processed image: {img_path}, label: {human_dir}")

    embeddings = np.array(embeddings)
    labels = np.array(labels)

    np.savez(os.path.join(destination_directory, 'db_embeddings.npz'), embeddings=embeddings, labels=labels)
    print(f"Database built successfully with {len(embeddings)} embeddings.")


if __name__ == "__main__":

    """
    1 - Recuperare le immagini da AlfaDocs (non si può)
    2 - Organizzare il DB locale usando patient_id come chiave
    3 - Calcolare gli embedding-Done
    4 - Fare recognition con quel DB locale-Done
    """
    # questa parte è in stallo perchè non posso prendere le immagini da AlfaDocs, ma una volta che le ho posso costruire il database locale e fare recognition 
    # db_directory = 'db_imgs_alfadocs'
    # destination_directory = 'db_embeddings_from_alfadocs'
    # collect_imgs_from_alfadocs(db_directory)


    db_directory = 'db_imgs'
    destination_directory = 'db_local_embeddings'
    build_embedding_database(db_directory, destination_directory)
    print("End script: Database built successfully.")

    

