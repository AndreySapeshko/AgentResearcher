from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory, Task, TaskStep, TaskStepStatus, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # обновляем username, если изменился
        if user.username != username:
            user.username = username
            await session.commit()
        return user

    # создаём нового пользователя
    user = User(
        telegram_id=telegram_id,
        username=username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_task(session: AsyncSession, user_id: int, title: str):
    task = Task(
        user_id=user_id,
        title=title,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def add_task_steps(session: AsyncSession, task_id: int, steps: list[str]):
    task_steps = [
        TaskStep(
            task_id=task_id,
            step_order=i,
            description=description,
        )
        for i, description in enumerate(steps, 1)
    ]

    session.add_all(task_steps)
    await session.commit()
    return task_steps


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
) -> TaskStep | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_step_by_id(
    session: AsyncSession,
    step_id: int,
) -> TaskStep | None:
    stmt = select(TaskStep).where(TaskStep.id == step_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_next_pending_step(session: AsyncSession, task_id: int):
    stmt = (
        select(TaskStep)
        .where(TaskStep.task_id == task_id)
        .where(TaskStep.status == TaskStepStatus.PENDING)
        .order_by(TaskStep.step_order.asc())
        .limit(1)
    )

    result = await session.execute(stmt)
    return result.scalars().first()


async def mark_step_in_progress(session: AsyncSession, step_id: int):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.IN_PROGRESS
    await session.commit()
    return task_step


async def update_step_result(session: AsyncSession, step_id: int, result: str):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.DONE
    task_step.result = result
    await session.commit()
    return task_step


async def mark_step_error(session: AsyncSession, step_id: int, error: str):
    task_step = await get_step_by_id(session, step_id)

    if not task_step:
        return None

    task_step.status = TaskStepStatus.ERROR
    task_step.result = error
    await session.commit()
    return task_step


async def get_completed_steps(session: AsyncSession, task_id: int):
    stmt = (
        select(TaskStep)
        .where(TaskStep.task_id == task_id)
        .where(TaskStep.status == TaskStepStatus.DONE)
        .order_by(TaskStep.step_order.asc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def save_memory(session: AsyncSession, task_id: int, content: str):
    task = await get_task_by_id(session, task_id)
    memory = Memory(
        user_id=task.user_id,
        content=content,
    )
    session.add(memory)
    await session.commit()
    return memory
