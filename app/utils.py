import cv2
import os
import aiohttp
from PIL import Image
from io import BytesIO
import face_recognition

from app.config import Config

async def fetch_image(url: str) -> Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": Config.USER_AGENT}) as response:
            if response.status == 200:
                image_data = await response.read()
                image = Image.open(BytesIO(image_data))
                return image
    return None

def save_image(image: Image, file_path: str):
    image.save(file_path)

def has_single_face(image: Image) -> bool:
    image_array = face_recognition.load_image_file(BytesIO(image.tobytes()))
    face_locations = face_recognition.face_locations(image_array)
    return len(face_locations) == 1

def has_single_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) == 1
