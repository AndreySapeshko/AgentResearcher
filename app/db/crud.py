from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Task, TaskStep


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
