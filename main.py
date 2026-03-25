import os

from db_builder import build_embedding_database
from cam_recognition import cam_recognition
import cv2



if __name__ == "__main__":

    db_directory = 'db_imgs'
    destination_directory = 'db_local_embeddings'
    debug_frames = 'debug_frames'

    cap = cv2.VideoCapture("test_video2.mp4")
    
    build_embedding_database(db_directory, destination_directory)
    cam_recognition(destination_directory, cap, debug_frames)