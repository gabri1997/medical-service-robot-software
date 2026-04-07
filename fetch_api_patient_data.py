import os
import requests
from datetime import datetime, timedelta
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID


def check_appointment_time(appointment):
    now = datetime.now()
    appt_datetime = datetime.strptime(appointment['date'], "%Y-%m-%d %H:%M:%S")

    diff = now - appt_datetime  

    if timedelta(minutes=-15) <= diff <= timedelta(minutes=15):
        print(f"Appointment ON TIME for patient {appointment['patientId']}")
        return 'on_time'
    
    elif diff < timedelta(minutes=-15):
        print(f"Appointment TOO EARLY for patient {appointment['patientId']}")
        return 'too_early'
    
    elif diff > timedelta(minutes=15):
        print(f"Appointment LATE for patient {appointment['patientId']}")
        return 'late'

def find_today_appointment(appointments, patient_id):
    if not appointments:
        print(f"No appointments found for patient {patient_id}.")
        return None, None
    today = datetime.today().date()
    today_app = []

    for appt in appointments:
        app_date = datetime.strptime(appt["date"], "%Y-%m-%d %H:%M:%S").date()
        if app_date == today:
            today_app.append(appt)
            print(f"Today's appointment for patient {patient_id}: {appt['id']} on {appt['date']}")
            # Se ha un appuntamento oggi chiamo la funzione che verifica se è in orario o no prendendo 15 minuti di tolleranza
            timing = check_appointment_time(appt)
    if not today_app:
        print(f"No appointments for patient {patient_id} today. Checking for closest appointment...") 
        return None, None
    return today_app, timing

def change_apointment_status(appointment, timing):
    if appointment is None:
        print("No appointment to update.")
        return
    
    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    status_mapping = {
        'on_time': 'waiting',
    }

    new_status = status_mapping.get(timing, 'scheduled')
    update_url = f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/appointments/{appointment[0]['id']}"
    
    payload = {
        "status": new_status
    }

    response = requests.put(update_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"Appointment {appointment[0]['id']} status updated to {new_status}.")
    else:
        print(f"Failed to update appointment {appointment[0]['id']} status. Status code: {response.status_code}")

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
    return patient_appointments


if __name__ == "__main__":
    
    patient_id = 101950247 # questo id lo prendo da cam_recognition, è la best_label che corrisponde al nome della cartella in cui ho messo le immagini del paziente, che a sua volta è l'id del paziente
    patient_appointments = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
    # Assumo nello scrivere il codice che ci siamo un solo appuntamento al giorno per ogni paziente
    today_appointment, timing = find_today_appointment(patient_appointments, patient_id)
    change_apointment_status(today_appointment, timing)