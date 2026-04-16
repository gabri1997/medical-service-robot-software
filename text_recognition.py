from faster_whisper import WhisperModel
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


if __name__ == '__main__':

    audio_pth = 'gabriele_rosati.mp3'
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments = recognizer(audio_pth, model)
    # ogni segmento contiene un testo trascritto, stampo il testo di ogni segmento
    full_text = " ".join(s.text for s in segments)
    normalized_name = text_normalization(full_text)

    print("Ecco il nome del paziente che ho riconosciuto:")
    print(normalized_name)