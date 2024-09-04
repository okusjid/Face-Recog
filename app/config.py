import os

class Config:
    IMAGES_DIR = os.getenv("IMAGES_DIR", "images")
    MAX_IMAGES = int(os.getenv("MAX_IMAGES", 300))
    USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
    GOOGLE_SEARCH_URL = "https://www.google.com/search?tbm=isch&q="
