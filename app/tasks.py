import os
from bs4 import BeautifulSoup
from app.config import Config
from .utils import fetch_image, save_image, has_single_face
import aiohttp
import cv2
import numpy as np
import asyncio

# Scrape high-quality image URLs from Google Image Search
async def scrape_high_quality_images(search_query: str, max_images: int = 300):
    search_url = f"{Config.GOOGLE_SEARCH_URL}{search_query.replace(' ', '+')}&tbm=isch"
    image_urls = []
    start = 0
    results_per_page = 20  # Adjust based on observation

    async with aiohttp.ClientSession() as session:
        while len(image_urls) < max_images:
            paginated_url = f"{search_url}&start={start}"
            async with session.get(paginated_url, headers={"User-Agent": Config.USER_AGENT}) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')

                    # CSS selector equivalent to your XPath
                    image_elements = soup.select('img')  # Select all image tags

                    for img_tag in image_elements:
                        img_url = img_tag.get('src') or img_tag.get('data-src')
                        if img_url and 'http' in img_url:
                            image_urls.append(img_url)
                            print(f"Found image URL: {img_url}")
                            if len(image_urls) >= max_images:
                                break

                    print(f"Found {len(image_urls)} image URLs.")

                    start += results_per_page

                if len(image_urls) >= max_images or len(soup.find_all('img')) == 0:
                    break

            await asyncio.sleep(1)  # Delay to avoid being blocked by Google

    return image_urls[:max_images]

# Main task to process images by downloading and saving them
async def process_images(task_input_name: str):
    query = task_input_name
    max_images = Config.MAX_IMAGES
    unprocessed_dir = os.path.join(Config.IMAGES_DIR, 'unprocessed')
    processed_dir = os.path.join(Config.IMAGES_DIR, 'processed')

    # Ensure directories exist
    os.makedirs(unprocessed_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # Fetch image URLs
    image_urls = await scrape_high_quality_images(query, max_images)
    saved_images = 0

    for idx, img_url in enumerate(image_urls):
        try:
            print(f"Fetching image {idx + 1}/{len(image_urls)}: {img_url}")
            image = await fetch_image(img_url)
            if image is None:
                print(f"Failed to fetch image: {img_url}")
                continue

            # Save the unprocessed image
            unprocessed_path = os.path.join(unprocessed_dir, f"{task_input_name}_{idx}.jpg")
            save_image(image, unprocessed_path)
            print(f"Unprocessed image saved at {unprocessed_path}")

            # Convert image to NumPy array for OpenCV processing
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Check for a single face in the image
            if has_single_face(image_np):
                processed_path = os.path.join(processed_dir, f"{task_input_name}_{idx}.jpg")
                save_image(image, processed_path)
                saved_images += 1
                print(f"Processed image saved at {processed_path}")

            # Stop if we've saved the maximum number of processed images
            if saved_images >= max_images:
                break

        except Exception as e:
            print(f"Failed to process image {img_url}: {str(e)}")

    print(f"Total images processed: {saved_images} out of {len(image_urls)}")

