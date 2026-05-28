
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
            "name": "fetch_api_patient_appointment", # qui chiaramente è fondamentale mantenere il nome della funzione presente
            "description": "Retrieve today's appointment for a patient",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": { # qui l'llm deve conoscere i parametri dinamici della funzione, in questo caso il patient_id che è l'output di cam_recognition o text_recognition, e che è fondamentale per fare la chiamata alle API per recuperare i dati del paziente
                        "type": "integer",
                        "description": "Unique patient identifier"
                    }
                },
                "required": ["patient_id"]
            }
        }
    }
]