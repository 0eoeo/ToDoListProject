from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from models import Task
from schemas import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task: TaskCreate):
    db_task = Task(title=task.title, priority=task.priority, status="incomplete")
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_tasks(db: AsyncSession, status: str = None):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)
    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalars().first()


async def update_task(db: AsyncSession, task_id: int, task: TaskUpdate):
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    for var, value in vars(task).items():
        if value is not None:
            setattr(db_task, var, value)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int):
    result = await db.execute(delete(Task).where(Task.id == task_id))
    await db.commit()
    return result.rowcount
