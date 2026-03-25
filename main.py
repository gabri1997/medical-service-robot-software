import os
from config import API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID
from fetch_api_patient_data import fetch_api_patient_data
from db_builder import build_embedding_database
from cam_recognition import cam_recognition
import cv2



if __name__ == "__main__":

    db_directory = 'db_imgs'
    destination_directory = 'db_local_embeddings'
    debug_frames = 'debug_frames'
    video_folder = 'test_video'

    video_path = os.path.join(video_folder, 'test_video2.mp4')
    cap = cv2.VideoCapture(video_path)
    
    build_embedding_database(db_directory, destination_directory)
    patient_id = cam_recognition(destination_directory, cap, debug_frames)
    fetch_api_patient_data(API_URL, API_KEY, PRACTICE_ID, ARCHIVE_ID, patient_id)