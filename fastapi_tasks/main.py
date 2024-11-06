from fastapi import FastAPI
from fastapi_tasks.database import engine, Base
from fastapi_tasks.routers import auth, tasks

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API"}