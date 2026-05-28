from llm_tools.wrappers import llm_execute_fetch_and_update, llm_identify_patient
# qua inizio a fare il routing alle funzioni di backend
# qui deve esserci il match con il nome della funzione presente nella descrizione del tool, è importante che il nome sia esattamente lo stesso per poter fare il routing corretto, ad esempio se il modello decide di chiamare fetch_api_patient_appointment allora qui devo avere un if che riconosce questo nome e chiama la funzione reale per prendere i dati del paziente, se invece il modello decide di chiamare un'altra funzione allora qui devo avere un altro if per riconoscere quel nome e chiamare la funzione corrispondente, ecc.
# poi nel tool schema devo mettere il nome del wrapper

def dispatch_tool_call(function_name,parsed_arguments):

    if function_name == "llm_execute_fetch_and_update":

        patient_id = parsed_arguments.get("patient_id")
        print(f"\nPatient ID to fetch data for: {patient_id}")
        result = llm_execute_fetch_and_update(patient_id)
        print(f"\nResult from TOOL function: {result}")
        return result
    
    if function_name == "llm_identify_patient":

        patient_id = llm_identify_patient()
        print(f"\nResult from TOOL function: {patient_id}")
        return patient_id

    raise ValueError(f"Unknown tool: {function_name}")