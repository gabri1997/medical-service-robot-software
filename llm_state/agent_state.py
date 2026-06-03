class AgentState:

    def __init__(self):

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for a medical service robot. Your task is to assist the robot in understanding user intents, resolving ambiguities, selecting actions, maintaining conversational state, and providing human-like fallbacks when necessary."
                )
            }
        ]

        self.current_mode = 'idle'
        # aggiungiamo un goal, quello che il robto cerca di ottenere
        self.current_goal = None

        # patient info 
        self.patient_id = None
        # appointment info
        self.appointment_timing = None
        self.appointment_status = None
        # session info 
        self.session_active = True # questo attributo mi serve per capire se la conversazione con l'utente è ancora attiva o no 
        # intent info
        self.current_intent = None
       


    def add_message(self, role, content):

            self.messages.append({
                "role": role,
                "content": content
        })
    
    # questa funzione servirà quando vorrò resettare lo stato dell'agente una volta terminata la conversazione
    def reset(self):

        self.patient_id = None
        
        self.appointment_timing = None
        self.appointment_status = None

        self.session_active = False

        self.current_intent = None

        