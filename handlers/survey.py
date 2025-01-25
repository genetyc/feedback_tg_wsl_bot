from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from states import Survey
from json_handler import msgs, answrs
from kb_generator import kb_generation, spec_kb_generation, multiple_choice_kb_generation

#'✅'
survey_router = Router()
active_state = None
#choice_cb = CallbackData()
temp = []


@survey_router.message(Survey.question1)
async def state1(message: Message, state: FSMContext):
    global active_state
    active_state = Survey.question2
    print(message.text)
    await state.set_state(Survey.question2)
    await message.answer(f"{msgs['where_you_found_out']}", reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text=i) for i in str(answrs['where_you_found_out']).split('=')]
    ]))


@survey_router.message(Survey.question2)
async def state2(message: Message, state: FSMContext):
    await message.answer(f"{msgs['what_is_quality_edu']}", reply_markup=spec_kb_generation(answrs['what_is_quality_edu'], True))
    await state.set_state(Survey.question3)
    
  
# @survey_router.callback_query()
# async def multiple_choice_state(callback: CallbackQuery, state: FSMContext):
#     print("button punched - ", callback.data)
#     if callback.data == 'next':
#         await callback.message.answer(f"{msgs['whats_your_goal']}", reply_markup=multiple_choice_kb_generation(answrs['whats_your_goal']))
#         await state.set_state(Survey.question3)


@survey_router.message(Survey.question3)
async def state3(message: Message, state: FSMContext):
    print(message.text)
    if message.text == 'Дальше':
        await message.answer(f"{msgs['whats_your_goal']}", reply_markup=spec_kb_generation(answrs['whats_your_goal'], True))
        await state.set_state(Survey.question4)


@survey_router.message(Survey.question4)
async def state4(message: Message, state: FSMContext):
    if message.text == 'Дальше':
        questions = str(msgs['education_quality']).split('-')
        await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
        await state.set_state(Survey.interstate)
        await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='your_thoughts', next_state=Survey.question5)


@survey_router.message(Survey.question5)
async def state5(message: Message, state: FSMContext):
    await message.answer(str(msgs['how_effective']))
    await state.set_state(Survey.question6)


@survey_router.message(Survey.question6)
async def state6(message: Message, state: FSMContext):
    questions = str(msgs['teacher_student']).split('-')
    await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
    await state.set_state(Survey.interstate)
    await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='professionalism', next_state=Survey.question8, mk='education_quality')


@survey_router.message(Survey.question7)    # TODO вот тут надо исправить
async def state7(message: Message, state: FSMContext):
    #await message.answer(msgs['professionalism'], reply_markup=spec_kb_generation(answrs['education_quality']))
    await state.set_state(Survey.question8)


@survey_router.message(Survey.question8)
async def state8(message: Message, state: FSMContext):
    await message.answer(msgs['other_events'], reply_markup=spec_kb_generation(answrs['other_events'], next_button=True))
    await state.set_state(Survey.question9)


@survey_router.message(Survey.question9)
async def state9(message: Message, state: FSMContext):
    if message.text == 'Дальше':
        await message.answer(msgs['teacher_parents'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(Survey.question10)


@survey_router.message(Survey.question10)
async def state10(message: Message, state: FSMContext):
    await message.answer(msgs['whats_good'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    print("state 10 ", message.text)
    await state.set_state(Survey.question11)


@survey_router.message(Survey.question11)
async def state11(message: Message, state: FSMContext):
    await message.answer(msgs['whats_bad'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    print("state 11 ", message.text)
    await state.set_state(Survey.question12)


@survey_router.message(Survey.question12)
async def state12(message: Message, state: FSMContext):
    await message.answer(msgs['your_wishes'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    print("state 12 ", message.text)
    await state.set_state(Survey.question13)


@survey_router.message(Survey.question13)
async def state13(message: Message, state: FSMContext):
    await message.answer(msgs['gender'], reply_markup=spec_kb_generation(answrs['gender']))
    print("state 13 ", message.text)
    await state.set_state(Survey.question14)


@survey_router.message(Survey.question14)
async def state14(message: Message, state: FSMContext):
    await message.answer(msgs['age'], reply_markup=spec_kb_generation(answrs['age']))
    print("state 14 ", message.text)
    await state.set_state(Survey.question15)


@survey_router.message(Survey.question15)
async def state15(message: Message, state: FSMContext):
    await message.answer(msgs['education'], reply_markup=spec_kb_generation(answrs['education']))
    print("state 15 ", message.text)
    await state.set_state(Survey.question16)


@survey_router.message(Survey.question16)
async def state16(message: Message, state: FSMContext):
    await message.answer(msgs['ending'], reply_markup=ReplyKeyboardRemove())
    print("state 16 ", message.text)


@survey_router.message(Survey.interstate)
async def interstate(message: Message, state: FSMContext):
    data = await state.get_data()
    counter = data['counter']
    phase = data['phase']
    questions = data['questions']
    next_q = data['next_q']
    next_state = data['next_state']
    try: mk = data['mk'] 
    except: mk = False
    if counter > 0:
        await message.answer(questions[phase], reply_markup=spec_kb_generation(answrs['education_quality'])) # магическая константа - чтобы избежать дублирования кода
        await state.update_data(counter=counter-1, phase=phase+1)
    else:
        await message.answer(f"{msgs[next_q]}", reply_markup=ReplyKeyboardRemove() if not mk else spec_kb_generation(answrs[mk]))
        await state.set_state(next_state)