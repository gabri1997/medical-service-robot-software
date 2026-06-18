from insightface.app import FaceAnalysis
from cam_recognition import identify_from_image
from fetch_api_patient_data import execute_fetch_and_update
from text_recognition import execute_text_recognition
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File
import numpy as np
from faster_whisper import WhisperModel
from local_db_builder import db_creation
from fastapi import UploadFile, File
from PIL import Image
import io
import os
from scheduler import scheduler, nightly_refresh
import time 

global patient_id
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(
    BASE_DIR,
    "patient_data.db"
)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "db_local_embeddings",
    "db_embeddings.npz"
)

DB = np.load(EMBEDDINGS_FILE)
face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

TEMP_AUDIO_FILE = os.path.join(
    BASE_DIR,
    "temp_audio.webm"
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)
model = WhisperModel("base", device="cpu", compute_type="int8")


if not os.path.exists(DB_FILE):
    db_creation(DB_FILE)
else:
    print("Database già esistente, procedo con il riconoscimento del paziente ...")
    
patient_id = None


def reload_embeddings():
    global DB
    DB = np.load(EMBEDDINGS_FILE)
    print("Embeddings reloaded")

def nightly_job():
    nightly_refresh()
    reload_embeddings()
 
scheduler.add_job(
    nightly_job,
    trigger="cron",
    hour=2,
    minute=0
)
print("Nightly refresh scheduled at 02:00 Europe/Rome")
scheduler.start()
app = FastAPI()

print("API FILE LOADED")
STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/identify")
async def identify(file: UploadFile = File(...)):

    global patient_id

    image_bytes = await file.read()

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    image = np.array(image)

    print(f"Received image of shape: {image.shape}")
    print(f"Image dtype: {image.dtype}")
    
    result = identify_from_image(
        face_app,
        DB,
        image
    )
    print(f"Identification result: {result}")
    if result is not None:
        patient_id = result["patient_id"]
        name = result["name"]
        surname = result["surname"]
        print(f"Identified patient ID: {patient_id}, Name: {name}, Surname: {surname}")
    return result


@app.post("/checkin")
def checkin():

    global patient_id

    if patient_id is None:
        return {
            "success": False,
            "message": "Nessun paziente identificato"
        }

    return execute_fetch_and_update(
        patient_id
    )

@app.post("/reset")
def reset():

    global patient_id
    patient_id = None

    return {
        "success": True,
        "message": "Stato resettato"
    }   

@app.post("/voice-identify")
async def voice_identify(
    file: UploadFile = File(...)
):
    global patient_id
    audio_bytes = await file.read()

    with open(
        TEMP_AUDIO_FILE,
        "wb"
    ) as f:

        f.write(audio_bytes)
    t0 = time.time()
    patient_id, name, surname = execute_text_recognition(
        TEMP_AUDIO_FILE,
        model,
        DB_FILE
    )
    print(f"Tempo totale: {time.time()-t0:.2f}s")
    print(f"Identified patient ID: {patient_id}, Name: {name}, Surname: {surname}")
    return {
        "patient_id": patient_id,
        "name": name,
        "surname": surname
    }