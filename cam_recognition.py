import cv2
import os 
import pathlib
import numpy as np
from insightface.app import FaceAnalysis

def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cam_recognition(db_embeddings_path, cap, debug_frames):

    if not os.path.exists(db_embeddings_path):
        print(f"Database embeddings not found at {db_embeddings_path}. Please build the database first.")
        return None, None
    else:
        print(f"Loading database embeddings from {db_embeddings_path}...")

    embedding = np.load(os.path.join(db_embeddings_path, 'db_embeddings.npz'))
    db_embeddings = embedding['embeddings']
    db_labels = embedding['labels']

    threshold = 0.5 # questa va capita

    # qui calcolo live gli embedding della webcam e li confronto con quelli del database, se la similarità è sotto la soglia allora è un match
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))


    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        faces = app.get(frame)

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            emb = face.embedding.astype(np.float32)
            emb = emb / np.linalg.norm(emb)

            sims = np.dot(db_embeddings, emb) / (np.linalg.norm(db_embeddings, axis=1) * np.linalg.norm(emb))
            best_idx = np.argmax(sims)
            best_score = sims[best_idx]
            best_label = db_labels[best_idx]

            if best_score > threshold:
                text = f"{best_label} ({best_score:.2f})"
            else:
                text = "Unknown"

            # la best label dipende dal nome della cartella in cui ho messo il gt, in questo caso deve essere il patient_id, così poi posso fare la chiamata alle API con quello stesso patient_id per recuperare i dati del paziente riconosciuto
            print(f"Best match: {best_label} with score {best_score:.2f}")

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # cv2.imshow('Face Recognition', frame)
        # if cv2.waitKey(1) == ord('q'):
        #     break

        if not os.path.exists(debug_frames):
            os.makedirs(debug_frames)

        cv2.imwrite(os.path.join(debug_frames, "debug_frame.jpg"), frame)
        cap.release()
        cv2.destroyAllWindows()

        return best_label, best_score



if __name__ == "__main__":

    db_embeddings_path = os.path.join('db_local_embeddings')
    cap = cv2.VideoCapture("test_video2.mp4")

    best_label, best_score = cam_recognition(db_embeddings_path, cap, debug_frames="debug_frames")
    print(f"Best match: {best_label} with score {best_score:.2f}")      
    
