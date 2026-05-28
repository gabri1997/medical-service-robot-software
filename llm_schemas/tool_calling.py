
"""
         LLM
          ↓
    tool selection
          ↓
 deterministic software
          ↓
      tool result
          ↓
LLM response generation
"""

# qui devo definire tutti i tool che il sistema LLM può usare, in pratica una descrizione machine-readable della funzione
# interfacce semantiche, sono la descrizione delle capacità del modello LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "llm_execute_fetch_and_update", # qui chiaramente è fondamentale mantenere il nome della funzione presente
            "description": "Retrieve today's appointment for a patient",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": { 
                        "description": "Unique patient identifier"
                    }
                },
                "required": ["patient_id"]
            }
        }
    },
    # questo tool serve per osservare il mondo in pratica, vede il pziente e capische chi è
    {
        "type": "function",
        "function": {
            "name": "llm_identify_patient", # qui chiaramente è fondamentale mantenere il nome della funzione presente
            "description": "Identify the patient based on available information, such as facial recognition and voice recognition",
            "parameters": {
                "type": "object",
                "properties": {
                    
                    },
                "required": [] # qui non si richiede nulla perchè l'id_patient sarà l'output di qeuesto tool 
                }
                
            }
        }
    
]