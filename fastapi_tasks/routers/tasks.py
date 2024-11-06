from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi_tasks import models, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.Task)
def create_task(user_id: int, task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[schemas.Task])
def read_tasks(user_id: int, page: int = 1, limit: int = 10, db: Session = Depends(database.get_db)):
    skip = (page - 1) * limit
    tasks = db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()
    return tasks

# @router.get("/", response_model=List[schemas.Task])
# async def read_tasks(user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(database.get_async_db)):
#     query = await db.execute(
#         models.Task.select().filter(models.Task.owner_id == user_id).offset(skip).limit(limit)
#     )
#     tasks = query.scalars().all()
#     return tasks


@router.delete("/{task_id}")
def delete_task(user_id: int, task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(user_id: int, task_id: int, task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.model_dump().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task