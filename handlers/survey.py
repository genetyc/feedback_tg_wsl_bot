from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from states import Survey
from handlers.json_handler import msgs, answrs
from keyboards.kb_generator import kb_generation, spec_kb_generation
from bot_create import db, admins


survey_router = Router()


@survey_router.message(Survey.question1)
async def state1(message: Message, state: FSMContext):
    text = message.text
    if text in ['Да', 'Нет']:
        await db.update(message.from_user.id, 'did_get_parents_report', False if text == 'Нет' else True)
    await state.set_state(Survey.question2)
    await message.answer(f"{msgs['where_you_found_out']}", reply_markup=spec_kb_generation(answrs['where_you_found_out']))


@survey_router.message(Survey.question2)
async def state2(message: Message, state: FSMContext):
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question3, questions='what_is_quality_edu', answers='what_is_quality_edu', next_button=False, current_question='where_you_found_out')
    else:
        if text in answrs['where_you_found_out']:
            await db.update(message.from_user.id, 'where_you_found_out', text)
        await message.answer(f"{msgs['what_is_quality_edu']}", reply_markup=spec_kb_generation(answrs['what_is_quality_edu'], next_button=False))
        await state.set_state(Survey.question3)


@survey_router.message(Survey.question3)
async def state3(message: Message, state: FSMContext):
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question3_5, questions='whats_your_goal', answers='whats_your_goal', next_button=False, current_question='what_is_quality_edu')
    else:
        if text in answrs['what_is_quality_edu']:
            await db.update(message.from_user.id, 'what_is_quality_edu', text)
        await message.answer(f"{msgs['whats_your_goal']}", reply_markup=spec_kb_generation(answrs['whats_your_goal'], next_button=False))
        await state.set_state(Survey.question3_5)
    

@survey_router.message(Survey.question3_5)
async def state3_5(message: Message, state: FSMContext):
    text = message.text
    temp_set = set()
    if text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question4, questions='nother', answers='whats_your_goal', next_button=False, tmp=True, temp_set = temp_set)
    else:
        if text in answrs['whats_your_goal']:
            temp_set.add(text)
        await message.answer(msgs['nother'], reply_markup=spec_kb_generation(answrs['whats_your_goal'], next_button=True))
        await state.set_state(Survey.question4)
        await state.update_data(temp_set=temp_set)
    

@survey_router.message(Survey.question4)
async def state4(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    temp_set = data['temp_set']
    if text in answrs['whats_your_goal'] and text != 'Другое':
        temp_set.add(text)
    if message.text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question4, questions='nother', answers='whats_your_goal', next_button=True, tmp=True, temp_set=temp_set)
    if message.text == 'Дальше':
        questions = str(msgs['education_quality']).split('=')
        await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
        await state.set_state(Survey.interstate)
        await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='your_thoughts', next_state=Survey.question5, temp_lst=[], current_question='education_quality')
        await db.update(message.from_user.id, 'whats_your_goal', ';'.join(temp_set))


@survey_router.message(Survey.question5)
async def state5(message: Message, state: FSMContext):
    await message.answer(str(msgs['how_effective']))
    text = message.text
    if text != 'Пропустить':
        await db.update(message.from_user.id, 'your_thoughts', text)
    await state.set_state(Survey.question6)


@survey_router.message(Survey.question6)
async def state6(message: Message, state: FSMContext):
    await db.update(message.from_user.id, 'how_effective', message.text)
    questions = str(msgs['teacher_student']).split('=')
    await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
    await state.set_state(Survey.interstate)
    await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='professionalism', next_state=Survey.question7, temp_lst=[], current_question='teacher_student', mk='education_quality')


@survey_router.message(Survey.question7)
async def state7(message: Message, state: FSMContext):
    text = message.text
    if text in answrs['education_quality']:
        await db.update(message.from_user.id, 'professionalism', text)
    await message.answer(msgs['other_events'], reply_markup=spec_kb_generation(answrs['other_events'], next_button=False))
    await state.set_state(Survey.question7_5)


@survey_router.message(Survey.question7_5)
async def state7_5(message: Message, state: FSMContext):
    text = message.text
    temp_set = set()
    if text in answrs['other_events2'] and text != 'Онлайн-интенсивы':
        temp_set.add(text)
        await message.answer(msgs['nother'], reply_markup=spec_kb_generation(answrs['other_events2'], next_button=True))
        await state.set_state(Survey.question8)
        await state.update_data(temp_set = temp_set)
    elif text == 'Онлайн-интенсивы':
        await message.answer("Напишите, какие онлайн-интенсивы Вам понравились больше всего:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question8, questions='nother', answers='other_events2', next_button=True, tmp=True, temp_set = temp_set)
    elif text == 'Ребёнок не участвовал':
        await db.update(message.from_user.id, 'other_events', 'Ребёнок не участвовал')
        await message.answer(msgs['teacher_parents'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(Survey.question9)


@survey_router.message(Survey.question8)
async def state8(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    temp_set = data['temp_set']
    if text in answrs['other_events'] and text != 'Онлайн-интенсивы':
        temp_set.add(text)
    elif text == 'Онлайн-интенсивы':
        await message.answer("Напишите, на какие онлайн-интенсивы вам понравились больше всего:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question8, questions='nother', answers='other_events2', next_button=True, tmp=True, temp_set=temp_set)
    elif message.text == 'Дальше':
        await db.update(message.from_user.id, 'other_events', ';'.join(temp_set))
        await message.answer(msgs['teacher_parents'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(Survey.question9)


@survey_router.message(Survey.question9)
async def state9(message: Message, state: FSMContext):
    text = message.text
    await db.update(message.from_user.id, 'teacher_parents', text)
    await message.answer(msgs['whats_good'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question10)


@survey_router.message(Survey.question10)
async def state10(message: Message, state: FSMContext):
    text = message.text
    if text != 'Пропустить':
        await db.update(message.from_user.id, 'whats_good', text)
    await message.answer(msgs['whats_bad'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question11)


@survey_router.message(Survey.question11)
async def state11(message: Message, state: FSMContext):
    text = message.text
    if text != 'Пропустить':
        await db.update(message.from_user.id, 'whats_bad', text)
    await message.answer(msgs['your_wishes'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question12)


@survey_router.message(Survey.question12)
async def state12(message: Message, state: FSMContext):
    text = message.text
    if text != 'Пропустить':
        await db.update(message.from_user.id, 'your_wishes', text)
    await message.answer(msgs['gender'], reply_markup=spec_kb_generation(answrs['gender']))
    await state.set_state(Survey.question13)


@survey_router.message(Survey.question13)
async def state13(message: Message, state: FSMContext):
    await message.answer(msgs['age'], reply_markup=spec_kb_generation(answrs['age']))
    await state.set_state(Survey.question14)
    text = message.text
    if text in answrs['gender']:
        await db.update(message.from_user.id, 'gender', text)


@survey_router.message(Survey.question14)
async def state14(message: Message, state: FSMContext):
    await message.answer(msgs['education'], reply_markup=spec_kb_generation(answrs['education']))
    await state.set_state(Survey.question15)
    text = message.text
    if text in answrs['age']:
        await db.update(message.from_user.id, 'age', text)


@survey_router.message(Survey.question15)
async def state15(message: Message, state: FSMContext):
    from datetime import date
    await message.answer(msgs['ending'], reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="До свидания")]
            ]))
    text = message.text
    tgid = message.from_user.id
    if text in answrs['education']:
        await db.update(tgid, 'education', text)
    await db.update(tgid, 'is_complete', True)
    await db.update(tgid, 'complete_date', date.today())
    await state.set_state(Survey.ending_state)


@survey_router.message(Survey.ending_state)
async def ending_state(message: Message, state: FSMContext):
    text = message.text
    if text == 'До свидания':
        kb_list = [
            [KeyboardButton(text='Оценить качество обучения'), KeyboardButton(text='Пройти опрос')]
        ]
        if message.from_user.id in admins:
            kb_list.append([KeyboardButton(text='Админ-панель')])
        await message.answer('Главная панель', reply_markup=kb_generation(kb_list=kb_list))
        await state.set_state(Survey.init_state)


@survey_router.message(Survey.interstate)
async def interstate(message: Message, state: FSMContext):
    data = await state.get_data()
    counter = data['counter']
    phase = data['phase']
    questions = data['questions']
    next_q = data['next_q']
    next_state = data['next_state']
    lst = data['temp_lst']
    current_question = data['current_question']
    try: mk = data['mk'] 
    except: mk = False
    text = message.text
    if counter > 0:
        await message.answer(questions[phase], reply_markup=spec_kb_generation(answrs['education_quality'])) # магическая константа - чтобы избежать дублирования кода
        await state.update_data(counter=counter-1, phase=phase+1, temp_lst=lst)
        if text in answrs['education_quality']:
            lst.append(text)
        else:
            lst.append('UNKNOWN')
    else:
        if text in answrs['education_quality']:
            lst.append(text)
        else:
            lst.append('UNKNOWN')
        await db.update(message.from_user.id, current_question, ';'.join(lst))
        await message.answer(f"{msgs[next_q]}", reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text="Пропустить")]]) if not mk else spec_kb_generation(answrs[mk]))
        await state.set_state(next_state)

    
@survey_router.message(Survey.other_state)
async def other_state(message: Message, state: FSMContext):
    data = await state.get_data()
    active_state = data['active_state']
    questions = data['questions']
    answers = data['answers']
    next_button = data['next_button']
    try:
        tmp = data['tmp'] 
        temp_set = data['temp_set']
    except:
        tmp = False
        current_question = data['current_question']
    text = message.text
    if not tmp:
        await db.update(message.from_user.id, current_question, text)
    else:
        if text != 'Другое':
            temp_set.add(text)
    await message.answer(f"{msgs[questions]}",reply_markup=spec_kb_generation(answrs[answers], next_button=next_button))
    await state.set_state(active_state)
    if tmp:
        await state.update_data(temp_set=temp_set)