from faster_whisper import WhisperModel
import Levenshtein
import sqlite3
import os



def recognizer(audio_pth, model):

    print("Modello caricato")
    audio_path = os.path.join(os.path.dirname(__file__), audio_pth)
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    return segments

def text_normalization(text):
    # implementa qui la logica di normalizzazione del testo, ad esempio rimuovendo spazi extra, convertendo in minuscolo, ecc.
    normalized_text = text.strip().lower()
    stopwords = [
    "ciao", "salve", "sono", "mi chiamo", "io sono",
    "buongiorno", "buonasera", "grazie", "nome", "cognome", "il mio nome è", "il mio cognome è", "il mio nome", "il mio cognome"
    ]
    for w in stopwords:
        normalized_text = normalized_text.replace(w, "")
    return normalized_text

def similarity(text1, text2):
    # usiamo la levenshtein distance come metrica di similarità testuale, più è bassa più i testi sono simili
    distance = Levenshtein.distance(text1, text2)
    max_len = max(len(text1), len(text2))
    if max_len == 0:
        return 1.0
    return 1 - distance / max_len   

def search_patient_in_local_db(normalized_name, db_flile):
    # implementa qui la logica per cercare nel database locale il paziente più simile al nome normalizzato, ad esempio utilizzando una metrica di similarità testuale come la distanza di Levenshtein o la similarità coseno tra vettori di parole
    patient_id = ''
    # interroga il database locale per trovare il paziente più simile al nome normalizzato, ad esempio utilizzando una query SQL o un algoritmo di ricerca
    # prima uso una query SQL per prendere tutti i nomi normalizzati dei pazienti dal database, poi calcolo la similarità tra il nome normalizzato riconosciuto e i nomi normalizzati dei pazienti, infine prendo il paziente con la similarità più alta
    connection = sqlite3.connect(db_flile)
    cursor = connection.cursor()
    cursor.execute("SELECT patient_id, full_normalized_name FROM patients")
    rows = cursor.fetchall()
    best_score = 0.0
    for row in rows:
        db_patient_id = row[0]
        db_normalized_name = row[1]
        # calcola la similarità tra il nome normalizzato riconosciuto e il nome normalizzato del paziente nel database, ad esempio utilizzando la distanza di Levenshtein o la similarità coseno tra vettori di parole
        score = similarity(normalized_name, db_normalized_name)
        if score > best_score:
            best_score = score
            patient_id = db_patient_id
    return patient_id

def execute_text_recognition(audio_pth, model, db_file):
    segments = recognizer(audio_pth, model)
    full_text = " ".join(s.text for s in segments)
    normalized_name = text_normalization(full_text)
    print(f"Ecco il nome del paziente che ho riconosciuto: {normalized_name}")
    patient_id = search_patient_in_local_db(normalized_name, db_file)
    return patient_id

if __name__ == '__main__':

    audio_pth = 'gabriele_rosati.mp3'
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments = recognizer(audio_pth, model)
    # ogni segmento contiene un testo trascritto, stampo il testo di ogni segmento
    full_text = " ".join(s.text for s in segments)
    normalized_name = text_normalization(full_text)

    print("Ecco il nome del paziente che ho riconosciuto:")
    print(normalized_name)