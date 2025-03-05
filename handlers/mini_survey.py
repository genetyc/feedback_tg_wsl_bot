from io import TextIOWrapper
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from states import MiniSurvey
from handlers.json_handler import msgs, answrs
from keyboards.kb_generator import spec_kb_generation, rates_kb_generation


mini_survey_router = Router()
current_question = 'edu_rating'
file: TextIOWrapper
user_is_angry: bool = False
anon: bool = False


@mini_survey_router.message(MiniSurvey.question0)
async def state0(message: Message, state: FSMContext):
    global file, current_question, anon
    file = open('testing_data_gather.txt', 'w')
    file.flush()
    text = message.text
    if text not in answrs['anon'].split('='):
        await message.answer("Некорректный ответ", reply_markup=spec_kb_generation(answrs['anon']))
        await state.set_state(MiniSurvey.question0)
    else:
        anon = text.endswith('анонимно')
    if not anon:
        await message.answer("Пожалуйста, напишите Ваше ФИО и номер телефона\n\nПример: 'Иванов Иван Иванович, 88120000000'", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.question0_1)
    else:
        await message.answer(f"{msgs['edu_rating']}", reply_markup=rates_kb_generation(1, 11))
        await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question0_1)
async def state0_1(message: Message, state: FSMContext):
    global file, current_question, anon
    text = message.text
    file.write(f'Contacts->{text}\n')
    await message.answer(f"{msgs['edu_rating']}", reply_markup=rates_kb_generation(1, 11))
    await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question1)
async def state1(message: Message, state: FSMContext):
    global file, current_question, user_is_angry
    text = message.text
    try: 
        text = int(text)
        isdigit = 1 <= text <= 10
    except: isdigit = False 
    if isdigit:
        file.write(f'{current_question}->{text}\n')
        if text <= 4:
            await state.set_state(MiniSurvey.question2_1)
            await message.answer(f"{msgs['whats_wrong']}", reply_markup=spec_kb_generation(answrs['whats_wrong']))
            current_question = 'whats_wrong'
            user_is_angry = True
            file.write('what_to_improve->EMPTY\n')
        elif text <= 7:
            await state.set_state(MiniSurvey.question2_2)
            await message.answer(f"{msgs['what_to_improve']}", reply_markup=ReplyKeyboardRemove())
            current_question = 'what_to_improve'
        else:
            await state.set_state(MiniSurvey.question3)
            await message.answer(f"{msgs['general_quality2']}", reply_markup=spec_kb_generation(answrs['general_quality']))
            current_question = 'general_quality'
    else:
        await message.answer("Некорректный ответ", reply_markup=rates_kb_generation(1, 11))
        await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question2_1)
async def state2_1(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        await state.update_data(active_state=MiniSurvey.question3, questions='general_quality', answers='general_quality')
    else:
        file.write(f'{current_question}->{text if text in answrs['whats_wrong'] else 'UNKNOWN'}\n')
        await message.answer(f'{msgs['general_quality']}', reply_markup=spec_kb_generation(answrs['general_quality']))
        await state.set_state(MiniSurvey.question3)
        current_question = 'general_quality'


@mini_survey_router.message(MiniSurvey.question2_2)
async def state2_2(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    file.write(f'whats_wrong->EMPTY\n')
    file.write(f'{current_question}->{text}\n')
    await message.answer(f'{msgs['general_quality']}', reply_markup=spec_kb_generation(answrs['general_quality']))
    await state.set_state(MiniSurvey.question3)
    current_question = 'general_quality'


@mini_survey_router.message(MiniSurvey.question3)
async def state3(message: Message, state: FSMContext):
    global file, current_question, user_is_angry
    text = message.text
    tmp_answers = answrs['general_quality'].split('=')
    if text not in tmp_answers:
        await message.answer("Некорректный ответ", reply_markup=spec_kb_generation(answrs['general_quality']))
        await state.set_state(MiniSurvey.question3)
    elif text == tmp_answers[4] or text == tmp_answers[3]:
        await message.answer("Что, по вашему мнению, мешает прогрессу?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        user_is_angry = True
        await state.update_data(active_state=MiniSurvey.question4, questions='would_u_share', answers='would_u_share')
    else:
        await message.answer(f'{msgs['would_u_share']}', reply_markup=spec_kb_generation(answrs['would_u_share']))
        await state.set_state(MiniSurvey.question4)
        current_question = 'would_u_share'
        file.write(f'{current_question}->{text}\n')


@mini_survey_router.message(MiniSurvey.question4)
async def state4(message: Message, state: FSMContext):
    global file, current_question
    current_question = 'would_u_share'
    text = message.text
    if text not in answrs[current_question]:
        await message.answer("Некорректный ответ, попробуйте снова", reply_markup=spec_kb_generation(answrs['would_u_share']))
    elif text == 'Нет':
        await message.answer("Пожалуйста, уточните, почему?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        current_question = 'why_not'
        await state.update_data(active_state=MiniSurvey.question5, questions='thanks', answers='thanks')
    else:
        await message.answer(f'{msgs['thanks']}', reply_markup=spec_kb_generation(answrs['thanks']))
        await state.set_state(MiniSurvey.question5)
        file.write(f'{current_question}->{text}\n')


@mini_survey_router.message(MiniSurvey.question5)
async def state5(message: Message, state: FSMContext):
    global file, current_question
    file.close()


@mini_survey_router.message(MiniSurvey.other_state)
async def other_state(message: Message, state: FSMContext):
    global file, current_question, temp
    data = await state.get_data()
    active_state = data['active_state']
    questions = data['questions']
    answers = data['answers']
    text = message.text
    file.write(f'{current_question}->{text}\n')
    await message.answer(f"{msgs[questions]}",reply_markup=spec_kb_generation(answrs[answers], next_button=False))
    await state.set_state(active_state)