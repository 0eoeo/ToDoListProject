from fastapi import FastAPI, HTTPException, Depends, APIRouter
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session, engine
from models import Base
from schemas import TaskCreate, TaskUpdate, Task
from crud import create_task, get_tasks, update_task, delete_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")


async def get_db():
    async with async_session() as session:
        yield session


@api_router.post("/tasks", response_model=Task)
async def create_task_endpoint(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = await create_task(db, task)
    return new_task


@api_router.get("/tasks", response_model=List[Task])
async def get_tasks_endpoint(status: str = None, db: AsyncSession = Depends(get_db)):
    tasks_list = await get_tasks(db, status)
    return tasks_list


@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task_endpoint(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    if not task.dict(exclude_unset=True):
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    updated_task = await update_task(db, task_id, task)
    if updated_task:
        return updated_task
    else:
        raise HTTPException(status_code=404, detail="Task not found.")


@api_router.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_task(db, task_id)
    if result:
        return {"message": "Task deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found.")


app.include_router(api_router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
