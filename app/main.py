from fastapi import FastAPI, Form, BackgroundTasks, HTTPException
from app.models import TaskInput
from app.tasks import scrape_images

app = FastAPI()

@app.post("/start-task/")
async def start_task(name: str = Form(...), background_tasks: BackgroundTasks = None):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    task_input = TaskInput(name=name)
    background_tasks.add_task(scrape_images, task_input)
    return {"message": "Task started successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
