import requests
import sqlite3
import os
from datetime import datetime, timedelta
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from notifier import notify_event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    timing  = []

    for appt in appointments:
        app_date = datetime.strptime(appt["date"], "%Y-%m-%d %H:%M:%S").date()
        if app_date == today:
            today_app.append(appt)
            print(f"Today's appointment for patient {patient_id}: {appt['id']} on {appt['date']}")
            # Se ha un appuntamento oggi chiamo la funzione che verifica se è in orario o no prendendo 15 minuti di tolleranza
            app_timing = check_appointment_time(appt)
            timing.append(app_timing)

    if not today_app:
        print(f"No appointments for patient {patient_id} today. Checking for closest appointment...") 
        # Qui manca la parte in cui verifico se ha appuntamenti ad esempio nei prossimi 10 giorni o nei 10 giorni precedenti, manca quel ramo ma devo capre se ha senso
        return None, None
    return today_app, timing

def change_apointment_status(appointment, timing):
    if not appointment:
        print("No appointment to update.")
        return False

    headers = {
        'X-Api-Key': API_KEY,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    status_mapping = {
        'on_time': 'waiting',
        'late': 'waiting',
        'too_early': 'waiting'
    }

    # appointment = lista di dict; timing = lista parallela di stringhe
    # [(0, app1), (1, app2), ...]
    # x[1] + il secondo elemento della tupla, cioè l'appuntamento; x[1]['date'] è la data dell'appuntamento; datetime.strptime(x[1]['date'], "%Y-%m-%d %H:%M:%S") è la data dell'appuntamento convertita in oggetto datetime; abs(datetime.strptime(x[1]['date'], "%Y-%m-%d %H:%M:%S") - datetime.now()) è la differenza in tempo tra la data dell'appuntamento e il momento attuale; min(..., key=lambda x: abs(datetime.strptime(x[1]['date'], "%Y-%m-%d %H:%M:%S") - datetime.now())) è la tupla (indice, appuntamento) che ha la data più vicina al momento attuale
    indexed_appointments = list(enumerate(appointment))
    closest_idx, closest_appointment = min(
        indexed_appointments,
        key=lambda x: abs(
            datetime.strptime(x[1]['date'], "%Y-%m-%d %H:%M:%S") - datetime.now()
        )
    )

    closest_timing = timing[closest_idx] if isinstance(timing, list) and closest_idx < len(timing) else None
    new_status = status_mapping.get(closest_timing, 'scheduled')

    print(
        f"Updating appointment {closest_appointment['id']} for patient "
        f"{closest_appointment['patientId']} to status {new_status} ..."
    )
    update_url = (
        f"{API_URL}/practices/{PRACTICE_ID}/archives/{ARCHIVE_ID}/appointments/"
        f"{closest_appointment['id']}"
    )

    payload = {"state": new_status}
    response = requests.patch(update_url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Appointment {closest_appointment['id']} status updated to {new_status}.")
        return True, new_status

    print(f"Failed to update appointment {closest_appointment['id']} status. Status code: {response.status_code}")
    return False, None

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
    patient_appointments = [appt for appt in appointments["data"] if str(appt["patientId"]) == str(patient_id)]
    print(f"Patient {patient_id} has {len(patient_appointments)} appointments.")
    return patient_appointments

def get_patient_info_from_db(db_path, patient_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name, surname FROM patients WHERE patient_id = ?", (patient_id,))
    result = cursor.fetchone()
    if result:
        name, surname = result
        print(f"Patient info from DB - ID: {patient_id}, Name: {name}, Surname: {surname}")
        return name, surname
    else:
        print(f"No patient found in DB with ID: {patient_id}")
        return None, None

def execute_fetch_and_update(patient_id):
    patient_appointments = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
    today_appointment, timing = find_today_appointment(patient_appointments, patient_id)
    print(f"Appuntamento di oggi per il paziente {patient_id}: {today_appointment} alle {timing}")
    if today_appointment is None:
        print(f"Il paziente {patient_id} non ha appuntamenti oggi.")
        notify_event("patient has no appointments", {"patient_id": patient_id})
        return
    else:
        updated, new_status = change_apointment_status(today_appointment, timing)
    if not updated:
        print("Non sono riuscito ad aggiornare lo stato dell'appuntamento.")
        return
    # dovrei rifare il fetch dei dati del paziente per vedere se lo stato dell'appuntamento è stato aggiornato correttamente
    patient_appointments = fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)
    today_appointment, timing = find_today_appointment(patient_appointments, patient_id)
    print(f"Appuntamento con stato aggiornato di oggi per il paziente {patient_id}: {today_appointment} alle {timing}")
    
    # guardo nel db locale per prendere nome e cognome dle paziente da passare al notifier
    db_path = os.path.join(BASE_DIR, 'patient_data.db')
    name, surname = None, None
    if os.path.exists(db_path):
        name, surname = get_patient_info_from_db(db_path, patient_id)
    else:
        print(f"[DB] Database non trovato: {db_path}")

    notify_event("appointment_status_updated", {
        "patient_id": patient_id,
        "patient_name": name if name else None,
        "patient_surname": surname if surname else None,
        "new_status": new_status
    })
    


if __name__ == "__main__":
    
    patient_id = 101950247 # questo id lo prendo da cam_recognition, è la best_label che corrisponde al nome della cartella in cui ho messo le immagini del paziente, che a sua volta è l'id del paziente
    execute_fetch_and_update(patient_id)
    