from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    init_state = State()
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


class MiniSurvey(StatesGroup):
    question0 = State()
    question0_1 = State()
    question1 = State()
    question2_1 = State()
    question2_2 = State()
    question2_3 = State()
    question3 = State()
    question4 = State()
    question5 = State()
    other_state = State()
