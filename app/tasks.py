import os
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from PIL import Image, UnidentifiedImageError
import numpy as np
import cv2
from io import BytesIO
from app.models import TaskInput
from app.utils import fetch_image, has_single_face
from app.config import Config

async def scrape_images(task_input: TaskInput):
    search_query = task_input.name.replace(' ', '+')
    url = f"{Config.GOOGLE_SEARCH_URL}{search_query}"
    
    unprocessed_dir = os.path.join(Config.IMAGES_DIR, 'unprocessed')
    processed_dir = os.path.join(Config.IMAGES_DIR, 'processed')
    
    os.makedirs(unprocessed_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    saved_images = 0

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": Config.USER_AGENT}) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            image_urls = [img.get('src') for img in soup.find_all('img') if img.get('src') and 'http' in img.get('src')]

            for i, img_url in enumerate(image_urls):
                try:
                    # Fetch the image data as bytes
                    image_data = await fetch_image(img_url)
                    if not image_data:
                        continue
                    
                    # Try to open the image with PIL to handle various formats
                    try:
                        image = Image.open(BytesIO(image_data))
                        image = image.convert('RGB')  # Ensure the image is in RGB format
                    except UnidentifiedImageError:
                        print(f"Error processing image {img_url}: cannot identify image file")
                        continue

                    # Save the unprocessed image
                    unprocessed_path = os.path.join(unprocessed_dir, f'{task_input.name}_{i}.jpg')
                    image.save(unprocessed_path)

                    # Convert image to NumPy array for OpenCV processing
                    image_np = np.array(image)

                    # Check if the image contains a single face
                    if has_single_face(image_np):
                        processed_path = os.path.join(processed_dir, f'{task_input.name}_{i}.jpg')
                        cv2.imwrite(processed_path, image_np)
                        saved_images += 1

                    if saved_images >= Config.MAX_IMAGES:
                        break
                except Exception as e:
                    print(f"Failed to process image {img_url}: {str(e)}")
                    continue
