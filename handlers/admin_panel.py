from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states import AdminPanel
from bot_create import db


admin_router = Router()


@admin_router.message(AdminPanel.admin_panel)
async def state0(message: Message, state: FSMContext):
    print(message.text)