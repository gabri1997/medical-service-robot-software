from openai import OpenAI
from dotenv import load_dotenv
import os

# Decido cosa fare in base al lingugio naturale dell'utente, ad esempio se l'utente dice "Sono arrivato" allora chiamo la funzione per prendere gli appuntamenti del paziente, se invece l'utente dice "Non riesco a trovarti nel sistema. Puoi ripetere lentamente il cognome?" allora chiedo di nuovo il nome al paziente e chiamo la funzione di riconoscimento vocale, ecc.
# LLM = decision layer, in praticha orchestra i tools deterministici del sistema, ad esempio le funzioni per il riconoscimento facciale, per la gestione degli appuntamenti, per la trascrizione vocale, ecc. e prendo decisioni su quale tool chiamare in base all'input dell'utente e allo stato della conversazione, ad esempio se riconosco un volto con alta confidenza allora prendo direttamente il patient_id e chiamo la funzione per prendere i dati del paziente, se invece non riconosco il volto o la confidenza è bassa allora chiedo il nome al paziente e chiamo la funzione di riconoscimento vocale e così via
# Python = execution layer

# Possibile esempio di interazioni ad alto livello fra LLM e componenti deterministici del sistema, ad esempio per la gestione degli appuntamenti:
# Utente:
# - "Sono arrivato"
# LLM decide:
# - "Devo chiamare fetch_appointment"
# Python esegue la funzione
# LLM genera risposta finale

# carico il file .env per accedere alle variabili d'ambiente, ad esempio la chiave API di OpenAI
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPEN_AI_API_KEY")
)

# conversazione base
messages = [
    # SYSTEM PROMPT: fornisce al modello informazioni sul suo ruolo, obiettivi e contesto che deve avere, è il cervello del sistema, è importante che sia ben definito e dettagliato per guidare il comportamento del modello in modo coerente con le esigenze del robot
    {"role": "system", "content": ("You are a helpful assistant for a medical service robot. Your task is to assist the robot in understanding user intents, resolving ambiguities, selecting actions, maintaining conversational state, and providing human-like fallbacks when necessary.")},    
    # USER PROMPT: rappresenta l'input dell'utente, ad esempio ciò che il paziente dice al robot, è importante che sia realistico e rappresentativo delle interazioni che il robot potrebbe avere con i pazienti
    {"role": "user", "content": "Ciao, sono Ettore Candeloro e sono arrivato un po' in anticipo al mio appuntamento."}]


# Chiamata API
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.3 # controllo del determinismo, se è basso le risposte saranno meno creative e deterministiche 
)

# Estrai risposta
assistant_reply = response.choices[0].message.content

print("\nAssistant:\n")
print(assistant_reply)
print("\nFull response object:\n")
print(response) # questa stampa mi serve per capire meglio cosa mi ritorna l'API, ad esempio se ci sono campi utili per il debug o per migliorare la conversazione, per capire usage, tokens e metadata
