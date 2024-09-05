from fastapi import FastAPI, Form, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from app.tasks import process_images
from app.config import Config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Ensure the images directories exist
if not os.path.exists(Config.IMAGES_DIR):
    os.makedirs(Config.IMAGES_DIR)

if not os.path.exists(os.path.join(Config.IMAGES_DIR, "unprocessed")):
    os.makedirs(os.path.join(Config.IMAGES_DIR, "unprocessed"))

if not os.path.exists(os.path.join(Config.IMAGES_DIR, "processed")):
    os.makedirs(os.path.join(Config.IMAGES_DIR, "processed"))

# Allow CORS from frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://172.16.5.147:5500"],  # Allows your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Serve the processed and unprocessed images statically
app.mount("/static", StaticFiles(directory=Config.IMAGES_DIR), name="static")

# POST endpoint to start the image scraping task
@app.post("/start-task/")
async def start_task(name: str = Form(...), background_tasks: BackgroundTasks = None):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    # Start the image processing task in the background
    background_tasks.add_task(process_images, name)
    return {"message": f"Task for '{name}' started successfully"}

# GET endpoint to fetch images (both processed and unprocessed)
@app.get("/get-images/")
async def get_images(query: str, type: str = Query("unprocessed")):
    if type == "unprocessed":
        directory = os.path.join(Config.IMAGES_DIR, 'unprocessed')
    elif type == "processed":
        directory = os.path.join(Config.IMAGES_DIR, 'processed')
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid type specified"})
    
    images = []
    for file_name in os.listdir(directory):
        if file_name.startswith(query):
            image_url = f"http://127.0.0.1:8000/static/{type}/{file_name}"
            images.append(image_url)

    if not images:
        return JSONResponse(status_code=404, content={"message": "No images found for this query"})
    
    return {"images": images}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
