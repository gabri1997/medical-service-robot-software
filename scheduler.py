from apscheduler.schedulers.background import BackgroundScheduler
from local_db_builder import db_creation
from collect_imgs_from_alfadocs import collect_imgs_from_alfadocs
from img_db_builder import build_embedding_database
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(
    BASE_DIR,
    "patient_data.db"
)

DB_IMGS_DIR = os.path.join(
    BASE_DIR,
    "db_imgs"
)
DB_DESTINATION_DIR = os.path.join(
    BASE_DIR,
    "db_local_embeddings"
)
def nightly_refresh():

    print("=== NIGHTLY REFRESH STARTED ===")

    try:

        db_creation(DB_FILE)

        collect_imgs_from_alfadocs(DB_IMGS_DIR)

        build_embedding_database(DB_IMGS_DIR, DB_DESTINATION_DIR)

        print("=== NIGHTLY REFRESH COMPLETED ===")

    except Exception as e:

        print(
            f"Nightly refresh failed: {e}"
        )


scheduler = BackgroundScheduler(
    timezone="Europe/Rome"
)
