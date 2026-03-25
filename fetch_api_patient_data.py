import os
import requests
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID


def fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id):

    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json'
    }
    
    # -------------------------------------------------------
    # print("Testing: List all patients...")
    # patients_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/patients"
    # response = requests.get(patients_url, headers=headers)
    # print(f"Status: {response.status_code}")

    # if response.status_code != 200:
    #     print("Failed to retrieve patients.")
    #     return
    
    # patients = response.json()
    # print(f"Found {patients['total']} patients.")
    # for patient in patients["results"]:
    #     patient_id = patient["id"]
    #     # 'results': [{'id': 101884589, 'firstName': 'GABRIELE', 'lastName': 'ROSATI', 'email': 'gabrielerosati97@gmail.com', 'emailEnabled': False, 'emailValid': True, 'phoneNumbers': [...], 'gender': None, 'street': None, 'city': None, 'postcode': None, 'province': '', 'dateBirth': None, 'placeOfBirth': None, 'italianFiscalCode': None, 'job': None, 'yearlyNumberingYear': None, 'yearlyNumberingNumber': None, 'defaultDiscount': None, ...}, {'id': 101950247, 'firstName': 'Ettore', 'lastName': 'Candeloro', 'email': 'ettorecandeloro@gmail.com', 'emailEnabled': False, 'emailValid': True, 'phoneNumbers': [...], 'gender': None, 'street': None, 'city': None, 'postcode': None, 'province': '', 'dateBirth': None, 'placeOfBirth': None, 'italianFiscalCode': None, 'job': None, 'yearlyNumberingYear': None, 'yearlyNumberingNumber': None, 'defaultDiscount': None, ...}]
    #     patient_name = patient["firstName"]
    #     patient_surname = patient["lastName"]
    #     print(f"Processing patient: {patient_name} {patient_surname} (ID: {patient_id})")
    #-------------------------------------------------------

    appointment_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/appointments"  
    response = requests.get(appointment_url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve appointments.")
        return

    appointments = response.json()
    print(f"Found {appointments['count']} appointments.")
    patient_appointments = [appt for appt in appointments["data"] if appt["patientId"] == patient_id]
    print(f"Patient {patient_id} has {len(patient_appointments)} appointments.")


if __name__ == "__main__":
    
    patient_id = 101950247 # questo id lo prendo da cam_recognition, è la best_label che corrisponde al nome della cartella in cui ho messo le immagini del paziente, che a sua volta è l'id del paziente
    patient_data = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
