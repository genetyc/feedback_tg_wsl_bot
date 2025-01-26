from io import TextIOWrapper
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from states import Survey
from json_handler import msgs, answrs
from kb_generator import kb_generation, spec_kb_generation
#from main import pool

#'✅'
survey_router = Router()
#choice_cb = CallbackData()
temp = set()
temp_list = []
current_question: str = 'did_receive_parents_report'
file: TextIOWrapper


@survey_router.message(Survey.question1)
async def state1(message: Message, state: FSMContext):
    global file, current_question
    file = open('testing_data_gather.txt', 'w')
    file.flush()
    await state.set_state(Survey.question2)
    await message.answer(f"{msgs['where_you_found_out']}", reply_markup=spec_kb_generation(answrs['where_you_found_out']))
    text = message.text
    if text == 'Да' or text == 'Нет':
        file.write(f'{current_question}->{text}\n')
    else:
        file.write(f'{current_question}->UNKNOWN\n')
    current_question = 'where_you_found_out'


@survey_router.message(Survey.question2)
async def state2(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question3, questions='what_is_quality_edu', answers='what_is_quality_edu', next_button=False)
    else:
        if text in answrs[current_question]:
            file.write(f'{current_question}->{text}\n')
        else:
            file.write(f'{current_question}->UNKNOWN\n')
        await message.answer(f"{msgs['what_is_quality_edu']}", reply_markup=spec_kb_generation(answrs['what_is_quality_edu'], False))
        await state.set_state(Survey.question3)
        current_question = 'what_is_quality_edu'


@survey_router.message(Survey.question3)
async def state3(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question4, questions='whats_your_goal', answers='whats_your_goal', next_button=True)
    else:
        if text in answrs[current_question]:
            file.write(f'{current_question}->{text}\n')
        else:
            file.write(f'{current_question}->UNKNOWN\n')
        await message.answer(f"{msgs['whats_your_goal']}", reply_markup=spec_kb_generation(answrs['whats_your_goal'], True))
        await state.set_state(Survey.question4)
        current_question = 'whats_your_goal'
    

@survey_router.message(Survey.question4)    # TODO можно написать еще одно сообщение 'что-то еще?', а в первом убрать кнопку дальше
async def state4(message: Message, state: FSMContext):
    global file, current_question, temp
    text = message.text
    if text in answrs[current_question]:
        temp.add(text)
    if message.text == "Другое":
        await message.answer("Предложите свой вариант:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question4, questions='whats_your_goal', answers='whats_your_goal', next_button=True, tmp=True)
    if message.text == 'Дальше':
        questions = str(msgs['education_quality']).split('-')
        await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
        await state.set_state(Survey.interstate)
        await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='your_thoughts', next_state=Survey.question5)
        try: temp.remove('Другое')
        except: pass
        file.write(f'{current_question}->{';'.join(temp)}\n')
        temp = set()
        current_question = 'education_quality'


@survey_router.message(Survey.question5)
async def state5(message: Message, state: FSMContext):
    global file, current_question
    await message.answer(str(msgs['how_effective']))
    text = message.text
    if text == 'Пропустить':
        file.write(f'{current_question}->EMPTY\n')
    else:
        file.write(f'{current_question}->{text}\n')
    await state.set_state(Survey.question6)
    current_question = 'how_effective'


@survey_router.message(Survey.question6)
async def state6(message: Message, state: FSMContext):
    global file, current_question
    file.write(f'{current_question}->{message.text}\n')
    questions = str(msgs['teacher_student']).split('-')
    await message.answer(questions[0], reply_markup=spec_kb_generation(answrs['education_quality']))
    await state.set_state(Survey.interstate)
    await state.update_data(counter=len(questions)-1, phase=1, questions=questions, next_q='professionalism', next_state=Survey.question8, mk='education_quality')


@survey_router.message(Survey.question8)
async def state8(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text in answrs['education_quality']:
        file.write(f'{current_question}->{text}\n')
    else:
        file.write(f'{current_question}->UNKNOWN\n')
    await message.answer(msgs['other_events'], reply_markup=spec_kb_generation(answrs['other_events'], next_button=True))
    await state.set_state(Survey.question9)
    current_question = 'other_events'


@survey_router.message(Survey.question9)
async def state9(message: Message, state: FSMContext):
    global file, current_question, temp
    text = message.text
    if text in answrs['other_events']:
        temp.add(text)
    if text == 'Онлайн-интенсивы':
        await message.answer("Напишите, на какие онлайн-интенсивы вам понравились больше всего:")
        await state.set_state(Survey.other_state)
        await state.update_data(active_state=Survey.question9, questions='other_events', answers='other_events2', next_button=True)
    elif message.text == 'Дальше' or message.text == 'Ребёнок не участвовал':
        try: temp.remove('Онлайн-интенсивы')
        except: pass
        try: 
            if len(temp) > 1:
                temp.remove('Ребёнок не участвовал')
        except: pass
        file.write(f'{current_question}->{';'.join(temp)}\n')
        temp = set()
        await message.answer(msgs['teacher_parents'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(Survey.question10)
        current_question = 'teacher_parents'


@survey_router.message(Survey.question10)
async def state10(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    file.write(f'{current_question}->{text}\n')
    await message.answer(msgs['whats_good'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question11)
    current_question = 'whats_good'


@survey_router.message(Survey.question11)
async def state11(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == 'Пропустить':
        file.write(f'{current_question}->EMPTY\n')
    else:
        file.write(f'{current_question}->{text}\n')
    await message.answer(msgs['whats_bad'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question12)
    current_question = 'whats_bad'


@survey_router.message(Survey.question12)
async def state12(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == 'Пропустить':
        file.write(f'{current_question}->EMPTY\n')
    else:
        file.write(f'{current_question}->{text}\n')
    await message.answer(msgs['your_wishes'], reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Пропустить')]
    ]))
    await state.set_state(Survey.question13)
    current_question = 'your_wishes'


@survey_router.message(Survey.question13)
async def state13(message: Message, state: FSMContext):
    global file, current_question
    text = message.text
    if text == 'Пропустить':
        file.write(f'{current_question}->EMPTY\n')
    else:
        file.write(f'{current_question}->{text}\n')
    await message.answer(msgs['gender'], reply_markup=spec_kb_generation(answrs['gender']))
    await state.set_state(Survey.question14)
    current_question = 'gender'


@survey_router.message(Survey.question14)
async def state14(message: Message, state: FSMContext):
    global file
    await message.answer(msgs['age'], reply_markup=spec_kb_generation(answrs['age']))
    await state.set_state(Survey.question15)
    text = message.text
    if text in str(answrs['gender']):
        file.write(f'gender->{text}\n')
    else:
        file.write(f'gender->UNKNOWN\n')


@survey_router.message(Survey.question15)
async def state15(message: Message, state: FSMContext):
    global file
    await message.answer(msgs['education'], reply_markup=spec_kb_generation(answrs['education']))
    await state.set_state(Survey.question16)
    text = message.text
    if text in str(answrs['age']):
        file.write(f'age->{text}\n')
    else:
        file.write(f'age->UNKNOWN\n')


@survey_router.message(Survey.question16)
async def state16(message: Message):
    global file
    await message.answer(msgs['ending'], reply_markup=ReplyKeyboardRemove())
    text = message.text
    if text in str(answrs['education']):
        file.write(f'education->{text}\n')
    else:
        file.write(f'education->UNKNOWN\n')
    file.close()


@survey_router.message(Survey.interstate)
async def interstate(message: Message, state: FSMContext):
    global file, current_question, temp_list
    data = await state.get_data()
    counter = data['counter']
    phase = data['phase']
    questions = data['questions']
    next_q = data['next_q']
    next_state = data['next_state']
    try: mk = data['mk'] 
    except: mk = False
    text = message.text
    if counter > 0:
        await message.answer(questions[phase], reply_markup=spec_kb_generation(answrs['education_quality'])) # магическая константа - чтобы избежать дублирования кода
        await state.update_data(counter=counter-1, phase=phase+1)
        if text in answrs['education_quality']:
            temp_list.append(text)
        else:
            temp_list.append('UNKNOWN')
    else:
        if text in answrs['education_quality']:
            temp_list.append(text)
        else:
            temp_list.append('UNKNOWN')
        file.write(f'{current_question}->{';'.join(temp_list)}\n')
        temp_list = []
        await message.answer(f"{msgs[next_q]}", reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text="Пропустить")]]) if not mk else spec_kb_generation(answrs[mk]))
        await state.set_state(next_state)
        current_question = next_q

    
@survey_router.message(Survey.other_state)
async def other_state(message: Message, state: FSMContext):
    global file, current_question, temp
    data = await state.get_data()
    active_state = data['active_state']
    questions = data['questions']
    answers = data['answers']
    next_button = data['next_button']
    try: tmp = data['tmp'] 
    except: tmp = False
    text = message.text
    if not tmp:
        file.write(f'{current_question}->{text}\n')
    else:
        temp.add(text)
    current_question = questions
    await message.answer(f"{msgs[questions]}",reply_markup=spec_kb_generation(answrs[answers], next_button=next_button))
    await state.set_state(active_state)