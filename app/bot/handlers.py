import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.agent.agent import ResearchPlanner
from app.agent.task_runner import TaskRunner
from app.db.crud import add_task_steps, create_task, get_or_create_user, get_user_by_telegram_id
from app.db.session import AsyncSessionLocal

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
        )

    await message.answer(
        f"👋 Привет!\n\n"
        f"Ты успешно зарегистрирован.\n"
        f"Твой ID: {user.telegram_id}\n"
        f"Имя: {user.username}\n"
        "AgentResearcher готов. 🚀\n"
        "Пришли задачу для исследования."
    )


@router.message()
async def handle_task(message: Message):
    telegram_id = message.from_user.id

    planner = ResearchPlanner()
    plan = await asyncio.to_thread(planner.plan, message.text)

    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, telegram_id)

        if not user:
            await message.answer("Сначала отправь /start, чтобы зарегистрироваться.")
            return

        task = await create_task(session, user.id, plan["title"])
        await add_task_steps(session, task.id, plan["steps"])

    await message.answer(
        "Я понял задачу и составил план:\n\n" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(plan["steps"]))
    )

    await message.answer("Начинаю выполнение задачи 🔍")

    runner = TaskRunner()
    await runner.run_task(session, task.id)

    await message.answer("Исследование завершено ✅")
