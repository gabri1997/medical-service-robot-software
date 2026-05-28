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

        # patient info 
        self.patient_id = None
        # appointment info
        self.appointment_timing = None
        self.appointment_status = None
        # session info 
        self.session_active = True # questo attributo mi serve per capire se la conversazione con l'utente è ancora attiva o no 

    def add_message(self, role, content):

            self.messages.append({
                "role": role,
                "content": content
        })