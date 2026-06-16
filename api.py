from insightface.app import FaceAnalysis
from cam_recognition import identify_from_image
from fetch_api_patient_data import execute_fetch_and_update
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File
import numpy as np
from fastapi import UploadFile, File
from PIL import Image
import io
import numpy as np

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

DB = np.load(
    "db_local_embeddings/db_embeddings.npz"
)

patient_id = None

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
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

    patient_id = result["patient_id"]

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