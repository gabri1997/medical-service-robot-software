import sys
import os
import json

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from openai import OpenAI
from dotenv import load_dotenv
from llm_schemas.tool_calling import tools # qui importo la lista dei tool che il modello può utilizzare, è importante che sia ben definita e aggiornata con tutte le funzioni che il sistema può eseguire, ad esempio le funzioni per il riconoscimento facciale, per la gestione degli appuntamenti, per la trascrizione vocale, ecc.
from llm_tools.wrappers import execute_fetch_and_update # qui importo la funzione wrapper che chiama la funzione reale per prendere i dati del paziente, è importante che questa funzione sia ben definita e aggiornata con tutte le funzionalità necessarie per interagire con le API del sistema, ad esempio gestire errori, formattare i dati, ecc.
from llm_orchestration.dispatcher import dispatch_tool_call # qui importo la funzione di dispatcher che fa il routing alle funzioni di backend in base al nome della funzione chiamata dal modello, è importante che questa funzione sia ben definita e aggiornata con tutte le funzionalità necessarie per fare il routing corretto, ad esempio riconoscere i nomi delle funzioni, gestire errori, ecc.
"""
___________________________________________________

SEMANTIC LAYER = LLM + tool schema + tool wrappers
___________________________________________________

Decido cosa fare in base al lingugio naturale dell'utente, ad esempio se l'utente dice "Sono arrivato" allora chiamo la funzione per prendere gli appuntamenti del paziente, se invece l'utente dice "Non riesco a trovarti nel sistema. Puoi ripetere lentamente il cognome?" allora chiedo di nuovo il nome al paziente e chiamo la funzione di riconoscimento vocale, ecc.
LLM = decision layer, in praticha orchestra i tools deterministici del sistema, ad esempio le funzioni per il riconoscimento facciale, per la gestione degli appuntamenti, per la trascrizione vocale, ecc. e prendo decisioni su quale tool chiamare in base all'input dell'utente e allo stato della conversazione, ad esempio se riconosco un volto con alta confidenza allora prendo direttamente il patient_id e chiamo la funzione per prendere i dati del paziente, se invece non riconosco il volto o la confidenza è bassa allora chiedo il nome al paziente e chiamo la funzione di riconoscimento vocale e così via
Python = execution layer

Possibile esempio di interazioni ad alto livello fra LLM e componenti deterministici del sistema, ad esempio per la gestione degli appuntamenti:
Utente:
- "Sono arrivato"
LLM decide:
- "Devo chiamare fetch_appointment"
Python esegue la funzione

LLM:
    - reasoning
    - orchestration
    - semantic understanding
Software:
    - execution
    - APIs
    - DB
    - side effects
    - security

# ARCHITETTURA MENTALE DEL SISTEMA:

        Speech
        ↓
        Whisper
        ↓
        Text
        ↓
        LLM reasoning
        ↓
        Tool selection (dispatcher e wrapper)
        ↓
        Python execution
        ↓
        Tool result
        ↓
        LLM response generation
        ↓
        TTS

    In particolare questo script dovrebbe fare:
        - create LLM request
        - receive tool call
        - pass tool call al dispatcher
        - receive result
        - observation injection
        - second LLM call


   
"""
# carico il file .env per accedere alle variabili d'ambiente, ad esempio la chiave API di OpenAI
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# conversazione base
messages = [
    # SYSTEM PROMPT: fornisce al modello informazioni sul suo ruolo, obiettivi e contesto che deve avere, è il cervello del sistema, è importante che sia ben definito e dettagliato per guidare il comportamento del modello in modo coerente con le esigenze del robot
    {"role": "system", "content": ("You are a helpful assistant for a medical service robot. Your task is to assist the robot in understanding user intents, resolving ambiguities, selecting actions, maintaining conversational state, and providing human-like fallbacks when necessary.")},    
    # USER PROMPT: rappresenta l'input dell'utente, ad esempio ciò che il paziente dice al robot, è importante che sia realistico e rappresentativo delle interazioni che il robot potrebbe avere con i pazienti
    {"role": "user", "content": "Quando è il mio appuntamento?"},
]

# devo definire un numero massimo di iterazioni per evitare loop infiniti
max_iterations = 5

"""
________________________________________________

La 'memoria del llm' è la conversation state reinjection
Ad ogni iterazione salvo lo stato della conversazione facendo l'append della risposta generata ai messages
e subito dopo rifaccio la create con quei messages aggiornati, in questo modo ho conversation state reinjection 
e il modello 'ricorda' di aver fatto determinate azioni, ad esempio se ha chiamato un tool specifico, e può utilizzare queste informazioni per generare risposte più accurate e contestualizzate
________________________________________________
"""

for iteration in range(max_iterations):
    print(f"\n--- Iteration {iteration + 1} ---\n")

    # Chiamata API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools, # qui passo la lista dei tool che il modello può utilizzare, è importante che sia ben definita e aggiornata con tutte le funzioni che il sistema può eseguire, ad esempio le funzioni per il riconoscimento facciale, per la gestione degli appuntamenti, per la trascrizione vocale, ecc.
        tool_choice="auto", # qui dico al modello di scegliere automaticamente quale tool utilizzare in base all'input dell'utente e allo stato della conversazione, è importante che il modello sia in grado di fare questa scelta in modo intelligente e coerente con le esigenze del robot, ad esempio se l'utente dice "Sono arrivato" allora il modello dovrebbe capire che deve chiamare la funzione per prendere gli appuntamenti del paziente, se invece l'utente dice "Non riesco a trovarti nel sistema. Puoi ripetere lentamente il cognome?" allora il modello dovrebbe capire che deve chiamare la funzione di riconoscimento vocale, ecc.
        temperature=0.3 # controllo del determinismo, se è basso le risposte saranno meno creative e deterministiche 
    )
    response_message = response.choices[0].message
    # Estrai risposta
    assistant_reply = response.choices[0].message.content

    print("\nAssistant:\n")
    print(assistant_reply)
    print("\nFull response object:\n")
    print(response) # questa stampa mi serve per capire meglio cosa mi ritorna l'API, ad esempio se ci sono campi utili per il debug o per migliorare la conversazione, per capire usage, tokens e metadata

    tool_calls = response_message.tool_calls or []
    if not tool_calls:
        print("\nNo tool calls made by the model. Ending conversation loop.")
        break # se il modello non chiama nessun tool allora esco dal loop, in questo modo evito di fare iterazioni inutili e posso gestire meglio i casi in cui il modello non riesce a capire l'intento dell'utente o a prendere decisioni corrette

    for tool_call in tool_calls:
        print("\nTool call made by the model:\n")
        function_name = tool_call.function.name
        print(f"Tool name: {function_name}")
        print(f"Tool arguments (raw): {tool_call.function.arguments}")
        # Gli argomenti del tool come dict Python
        parsed_arguments = json.loads(tool_call.function.arguments)
        print("\nPARSED ARGUMENTS:\n")
        print(parsed_arguments)

        """
        _________________________________________

        Routing delle mie funzioni di backend, ad esempio se il modello decide di chiamare fetch_api_patient_appointment allora qui devo avere un if che riconosce questo nome 
        e chiama la funzione reale per prendere i dati del paziente, 
        se invece il modello decide di chiamare un'altra funzione allora qui devo avere un altro if per riconoscere quel nome e chiamare la funzione corrispondente, ecc.
        Poi con il risultato ottenuto dalla funzione reale costruisco un nuovo messaggio di tipo "tool" che contiene il risultato della funzione, in questo modo faccio observation injection, 
        cioè dico al modello "Ecco il risultato della funzione che hai chiamato, 
        utilizza queste informazioni per rispondere alla domanda dell'utente"
        _________________________________________

        """
        # qua inizio a fare il routing alle funzioni di backend

        result = dispatch_tool_call(function_name, parsed_arguments) # qui chiamo la funzione di dispatcher che fa il routing alle funzioni di backend in base al nome della funzione chiamata dal modello, è importante che questa funzione sia ben definita e aggiornata con tutte le funzionalità necessarie per fare il routing corretto, ad esempio riconoscere i nomi delle funzioni, gestire errori, ecc.


        """
        ___________________________________________

        Observation injection, cioè dico al modello "Ecco il risultato della funzione 
        che hai chiamato, utilizza queste informazioni per rispondere alla domanda dell'utente",
        in questo modo il modello può utilizzare le informazioni ottenute dalla funzione per generare una risposta più accurata e 
        contestualizzata, ad esempio se l'utente chiede "Quando è l'appuntamento del paziente 101950247?" e il modello chiama fetch_api_patient_appointment con patient_id=101950247 
        e ottiene come risultato "L'appuntamento del paziente 101950247 è alle 15:00", allora quando il modello genera la risposta finale può utilizzare questa informazione 
        per rispondere correttamente alla domanda dell'utente, ad esempio "L'appuntamento del paziente 101950247 è alle 15:00"
        ___________________________________________


        """

        # qua costruisco observation memory e tool feedback loop
        # con questo il sisteam di conversazione diventa 'stateful' nel senso che lo stato della conversazione evolve nel tempo
        messages.append(response_message) # qua salvo la decisione/tool request fatta dal modello di chiamare fetch_api_patient_appointment con il patient_id specifico, in questo modo il modello 'ricorda' di aver fatto quella richiesta e può utilizzare questa informazione per generare la risposta finale, ad esempio se l'utente chiede "Quando è l'appuntamento del paziente 101950247?" e il modello chiama fetch_api_patient_appointment con patient_id=101950247, allora quando il modello genera la risposta finale può utilizzare le informazioni ottenute da fetch_api_patient_appointment per rispondere correttamente alla domanda dell'utente, ad esempio "L'appuntamento del paziente 101950247 è alle 15:00"
        # ora faccio observation injection, cioè dico al modello "Ecco il risultato della funzione che hai chiamato, utilizza queste informazioni per rispondere alla domanda dell'utente", in questo modo il modello può utilizzare le informazioni ottenute dalla funzione per generare una risposta più accurata e contestualizzata, ad esempio se l'utente chiede "Quando è l'appuntamento del paziente 101950247?" e il modello chiama fetch_api_patient_appointment con patient_id=101950247 e ottiene come risultato "L'appuntamento del paziente 101950247 è alle 15:00", allora quando il modello genera la risposta finale può utilizzare questa informazione per rispondere correttamente alla domanda dell'utente, ad esempio "L'appuntamento del paziente 101950247 è alle 15:00"
        messages.append({
            "role": "tool", # questo serve per far capire al modello che questo messaggio proviene da un tool
            "tool_call_id": tool_call.id,
            "content": json.dumps(result) # qua passo il risultato ottenuto dalla funzione reale, in questo modo faccio observation injection, cioè dico al modello "Ecco il risultato della funzione che hai chiamato, utilizza queste informazioni per rispondere alla domanda dell'utente"
            })
    
        print("\nUpdated messages with tool response:\n")
        for msg in messages:
            print(msg)