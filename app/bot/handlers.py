from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start_cmd(msg: Message):
    text = (
        "🚀 AgentResearcher готов. Пришли задачу для исследования."
    )
    await msg.answer(text)
