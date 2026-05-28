# qui metto i semantic wrappers attorno ai servizi reali del robot
# aggiungo un layer di astrazione che mi consente di nascondere dettagli quando faccio il routing alle funzioni di backend
"""
_______________________________________

Disaccoppiamento della logica di backend con la logica di orchestrazione LLM
In pratica separo semantica da infrastruttura nascondendo i dettagli del backend

_______________________________________

"""
from fetch_api_patient_data import execute_fetch_and_update
from main import identify_patient

def llm_execute_fetch_and_update(patient_id):

    result = execute_fetch_and_update(patient_id)
    return result

def llm_identify_patient():

    patient_id = identify_patient()
    return patient_id
    