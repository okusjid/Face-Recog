import aiohttp
import cv2
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import numpy as np
from app.config import Config

# Fetch the image from a URL using aiohttp and return a PIL Image
async def fetch_image(url: str) -> Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": Config.USER_AGENT}) as response:
            if response.status == 200:
                image_data = await response.read()
                try:
                    image = Image.open(BytesIO(image_data))
                    return image
                except UnidentifiedImageError:
                    print(f"Failed to identify image from {url}")
    return None

# Save the image to the specified file path
def save_image(image: Image, file_path: str):
    image.save(file_path)

# Detect if an image contains exactly one face using OpenCV
def has_single_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) == 1
