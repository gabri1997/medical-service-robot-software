# qui metto i semantic wrappers attorno ai servizi reali del robot
# aggiungo un layer di astrazione che mi consente di nascondere dettagli quando faccio il routing alle funzioni di backend
"""
_______________________________________

Disaccoppiamento della logica di backend con la logica di orchestrazione LLM
In pratica separo semantica da infrastruttura nascondendo i dettagli del backend

_______________________________________

"""
from fetch_api_patient_data import fetch_api_patient_data

def fetch_api_patient_appointment(patient_id):

    today_appointments = fetch_api_patient_data(patient_id)
    return today_appointments

