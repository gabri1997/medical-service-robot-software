from llm_tools.wrappers import fetch_api_patient_appointment, find_today_appointment
# qua inizio a fare il routing alle funzioni di backend
# qui deve esserci il match con il nome della funzione presente nella descrizione del tool, è importante che il nome sia esattamente lo stesso per poter fare il routing corretto, ad esempio se il modello decide di chiamare fetch_api_patient_appointment allora qui devo avere un if che riconosce questo nome e chiama la funzione reale per prendere i dati del paziente, se invece il modello decide di chiamare un'altra funzione allora qui devo avere un altro if per riconoscere quel nome e chiamare la funzione corrispondente, ecc.
# poi nel tool schema devo mettere il nome del wrapper

def dispatch_tool_call(function_name,parsed_arguments):

    if function_name == "fetch_api_patient_appointment":

        patient_id = parsed_arguments.get("patient_id")
        print(f"\nPatient ID to fetch data for: {patient_id}")
        patient_appointments = fetch_api_patient_appointment(patient_id)
        print(f"\nResult from TOOL function: {patient_appointments}")
        return patient_appointments
    

    raise ValueError(f"Unknown tool: {function_name}")