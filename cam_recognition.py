import cv2
import os 
import pathlib
import sqlite3
import numpy as np
from insightface.app import FaceAnalysis

def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# TODO
"""
Voglio:
    primo frame valido?
    miglior frame tra N?
Quando devo fermarmi?
    dopo N frame?
    dopo un certo score?
    dopo timeout?
 Se ho più volti nello stesso frame:
    quale scelgo?
"""

# qua definisco quanti frames devo processare, leggo massimo 120 frames e ne analizzo solo 1/3, quindi 40
# ma se trovo un frame con score alto con score di almeno 0.72 mi fermo subito
def cam_recognition(
    app,
    db_embeddings_path,
    cap,
    debug_frames,
    max_frames=120,
    process_every_n_frames=3,
    early_stop_score=0.70,
):

    if not os.path.exists(db_embeddings_path):
        print(f"Database embeddings not found at {db_embeddings_path}. Please build the database first.")
        return None, None
    else:
        print(f"Loading database embeddings from {db_embeddings_path}...")

    embedding = np.load(os.path.join(db_embeddings_path, 'db_embeddings.npz'))
    db_embeddings = embedding['embeddings']
    db_labels = embedding['labels']

    # qui calcolo live gli embedding della webcam e li confronto con quelli del database, se la similarità è sopra la soglia allora è un match
    app.prepare(ctx_id=0, det_size=(640, 640))

    frames_best_label = None
    frames_best_score = 0.0

    if max_frames <= 0:
        max_frames = 120
    if process_every_n_frames <= 0:
        process_every_n_frames = 1
  

    # qui il concetto è ritornare il migliore fra tutti i frames senza utilizzare una soglia 
    # poi vorrei utilizzare una soglia invece per far partire il riconoscimento da speech, se ad esempio il volto riconosciuto ha confidence bassa allora parte
    # devo testare la soglia sulla base dei dati del mio database e volendo :
    # soglia alta → accettazione immediata
    # soglia intermedia → candidato ambiguo, chiedi voce
    # soglia bassa → unknown

    frame_count = 0
    processed_frame_count = 0

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame_count += 1
        if frame_count % process_every_n_frames != 0:
            continue

        processed_frame_count += 1

        faces = app.get(frame)

        if not faces:
            continue

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            emb = face.embedding.astype(np.float32)
            emb = emb / np.linalg.norm(emb)

            sims = np.dot(db_embeddings, emb) / (np.linalg.norm(db_embeddings, axis=1) * np.linalg.norm(emb))
            best_idx = np.argmax(sims)
            best_score = sims[best_idx]
            best_label = db_labels[best_idx]

            text = f"{best_label} ({best_score:.2f})"

            if best_score > frames_best_score:
                frames_best_score = best_score
                frames_best_label = best_label
                # la best label dipende dal nome della cartella in cui ho messo il gt, in questo caso deve essere il patient_id, così poi posso fare la chiamata alle API con quello stesso patient_id per recuperare i dati del paziente riconosciuto
                print(f"Best match updated: {best_label} with score {best_score:.2f}")
                if not os.path.exists(debug_frames):
                    os.makedirs(debug_frames)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.imwrite(os.path.join(debug_frames, "best_debug_frame.jpg"), frame)

            else:
                print(f"Match found but not best: {best_label} with score {best_score:.2f}")
                
            if frames_best_score >= early_stop_score:
                print(
                    f"Early stop: best score {frames_best_score:.2f} >= {early_stop_score:.2f}"
                )
                break

        # cv2.imshow('Face Recognition', frame)
        # if cv2.waitKey(1) == ord('q'):
        #     break

        if frames_best_score >= early_stop_score:
            break

    print(
        f"Processed {processed_frame_count} sampled frames out of {frame_count} total (max {max_frames})."
    )
    
    cap.release()
    cv2.destroyAllWindows()

    return frames_best_label, frames_best_score

def get_patient_info_from_db(db_path, patient_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name, surname FROM patients WHERE patient_id = ?", (patient_id,))
    result = cursor.fetchone()
    if result:
        name, surname = result
        print(f"Patient info from DB - ID: {patient_id}, Name: {name}, Surname: {surname}")
        return name, surname
    else:
        print(f"No patient found in DB with ID: {patient_id}")
        return None, None


def identify_from_image(app, embedding, image):
    
    if image is None:
        print("No image provided for recognition.")
        return {
            "patient_id": None,
            "score": 0.0,
            "name": None,
            "surname": None
        }

    # image arriva da gradio e deve essere un numpy array
    faces = app.get(image)
    if not faces:
        print("No faces detected in the provided image.")
        return {
            "patient_id": None,
            "score": 0.0,
            "name": None,
            "surname": None
        }
    face = max(
        faces,
        key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1])
    )

    db_embeddings = embedding['embeddings']
    db_labels = embedding['labels']

    emb = face.embedding.astype(np.float32)
    emb = emb / np.linalg.norm(emb)
    sims = np.dot(db_embeddings, emb) / (np.linalg.norm(db_embeddings, axis=1) * np.linalg.norm(emb))
    best_idx = np.argmax(sims)
    best_score = float(sims[best_idx])
    if best_score < 0.5:
        print(f"Low confidence score: {best_score:.2f}. No reliable match found.")
        return {
            "patient_id": None,
            "score": best_score,
            "name": None,
            "surname": None
        }
    best_label = db_labels[best_idx]
    print(f"Best match: {best_label} with score {best_score:.2f}")
    name, surname = get_patient_info_from_db("patient_data.db", best_label)
    return {
        "patient_id": str(best_label),
        "score": float(best_score),
        "name": name,
        "surname": surname
    }
    

if __name__ == "__main__":

    db_embeddings_path = os.path.join('db_local_embeddings')
    cap = cv2.VideoCapture("test_video2.mp4")
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    best_label, best_score = cam_recognition(app, db_embeddings_path, cap, debug_frames="debug_frames")
    print(f"Best match: {best_label} with score {best_score:.2f}")      
    
