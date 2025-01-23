from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
