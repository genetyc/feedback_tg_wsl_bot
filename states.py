from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    input_state = State()
    question1 = State()
    question2 = State()
    question3 = State()
    question3_5 = State()
    question4 = State()
    question5 = State()
    question6 = State()
    question7 = State()
    question7_5 = State()
    question8 = State()
    question9 = State()
    question10 = State()
    question11 = State()
    question12 = State()
    question13 = State()
    question14 = State()
    question15 = State()
    interstate = State()
    other_state = State()
    nother_state = State()
