from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from states import Survey, MiniSurvey
from handlers.json_handler import msgs, answrs
from keyboards.kb_generator import kb_generation, spec_kb_generation, rates_kb_generation
from bot_create import db
from filters.is_admin import is_admin


mini_survey_router = Router()


@mini_survey_router.message(MiniSurvey.question0)
async def state0(message: Message, state: FSMContext):
    text = message.text
    if text not in answrs['anon'].split('='):
        await message.answer("Некорректный ответ", reply_markup=spec_kb_generation(answrs['anon']))
        await state.set_state(MiniSurvey.question0)
    elif not text.endswith('анонимно'):
        await message.answer("Пожалуйста, напишите Ваше ФИО и номер телефона\n\nПример: 'Иванов Иван Иванович, 88120000000'", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.question0_1)
    else:
        await message.answer(f"{msgs['edu_rating']}", reply_markup=rates_kb_generation(1, 11))
        await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question0_1)
async def state0_1(message: Message, state: FSMContext):
    text = message.text
    await db.update(message.from_user.id, 'contacts', text, minisurvey=True)
    await message.answer(f"{msgs['edu_rating']}", reply_markup=rates_kb_generation(1, 11))
    await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question1)
async def state1(message: Message, state: FSMContext):
    text = message.text
    try: 
        text = int(text)
        isdigit = 1 <= text <= 10
    except: isdigit = False 
    if isdigit:
        await db.update(message.from_user.id, 'edu_rating', text, minisurvey=True)
        if text <= 4:
            await state.set_state(MiniSurvey.question2_1)
            await message.answer(f"{msgs['whats_wrong']}", reply_markup=spec_kb_generation(answrs['whats_wrong']))
            await db.update(message.from_user.id, 'is_disappointed', True, minisurvey=True)
        elif text <= 7:
            await state.set_state(MiniSurvey.question2_2)
            await message.answer(f"{msgs['what_to_improve']}", reply_markup=ReplyKeyboardRemove())
        else:
            await state.set_state(MiniSurvey.question3)
            await message.answer(f"{msgs['general_quality2']}", reply_markup=spec_kb_generation(answrs['general_quality']))
    else:
        await message.answer("Некорректный ответ", reply_markup=rates_kb_generation(1, 11))
        await state.set_state(MiniSurvey.question1)


@mini_survey_router.message(MiniSurvey.question2_1)
async def state2_1(message: Message, state: FSMContext):
    text = message.text
    if text == "Другое":
        await message.answer("Предложите свой вариант:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        await state.update_data(active_state=MiniSurvey.question3, questions='general_quality', answers='general_quality', current_question='whats_wrong')
    else:
        if text in answrs['whats_wrong']: 
            await db.update(message.from_user.id, 'whats_wrong', text, minisurvey=True)
        await message.answer(f'{msgs['general_quality']}', reply_markup=spec_kb_generation(answrs['general_quality']))
        await state.set_state(MiniSurvey.question3)


@mini_survey_router.message(MiniSurvey.question2_2)
async def state2_2(message: Message, state: FSMContext):
    text = message.text
    await db.update(message.from_user.id, 'what_to_improve', text, minisurvey=True)
    await message.answer(f'{msgs['general_quality']}', reply_markup=spec_kb_generation(answrs['general_quality']))
    await state.set_state(MiniSurvey.question3)


@mini_survey_router.message(MiniSurvey.question3)
async def state3(message: Message, state: FSMContext):
    text = message.text
    tgid = message.from_user.id
    tmp_answers = answrs['general_quality'].split('=')
    if text not in tmp_answers:
        await message.answer("Некорректный ответ", reply_markup=spec_kb_generation(answrs['general_quality']))
        await state.set_state(MiniSurvey.question3)
    elif text == tmp_answers[4] or text == tmp_answers[3]:
        await message.answer("Что, по вашему мнению, мешает прогрессу?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        await db.update(tgid, 'is_disappointed', True, minisurvey=True)
        await db.update(tgid, 'general_quality', text, minisurvey=True)
        await state.update_data(active_state=MiniSurvey.question4, questions='would_u_share', answers='would_u_share', current_question='whats_stopping_progress')
    else:
        await message.answer(f'{msgs['would_u_share']}', reply_markup=spec_kb_generation(answrs['would_u_share']))
        await state.set_state(MiniSurvey.question4)
        await db.update(tgid, 'general_quality', text, minisurvey=True)


from datetime import date
@mini_survey_router.message(MiniSurvey.question4)
async def state4(message: Message, state: FSMContext):
    text = message.text
    tgid = message.from_user.id
    anon = '-' == await db.fetchval("SELECT contacts FROM public.mini_survey WHERE telegram_id = $1", tgid)
    is_disappointed = await db.fetchval("SELECT is_disappointed FROM public.mini_survey WHERE telegram_id = $1", tgid)
    if text not in answrs['would_u_share']:
        await message.answer("Некорректный ответ, попробуйте снова", reply_markup=spec_kb_generation(answrs['would_u_share']))
    elif text == 'Нет':
        await message.answer("Пожалуйста, уточните, почему?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.other_state)
        await db.update(tgid, 'would_u_share', text, minisurvey=True)
        if is_disappointed:
            await state.update_data(active_state=MiniSurvey.low_grade_state, questions='low_grade', answers='yn', current_question='why_not')
        else:
            await state.update_data(active_state=MiniSurvey.question5, questions='thanks', answers='thanks', current_question='why_not')
    else:
        await db.update(tgid, 'would_u_share', text, minisurvey=True)
        if not anon and not is_disappointed:
            await message.answer(f'{msgs['thanks']}', reply_markup=spec_kb_generation(answrs['thanks2']))
            await state.set_state(MiniSurvey.question5) # TODO нужно пофиксить отметку прохождения отчета
            await db.update(tgid, 'is_complete', True, minisurvey=True)
            await db.update(tgid, 'complete_date', date.today(), minisurvey=True)
        else:
            if is_disappointed:
                await message.answer(msgs['low_grade'], reply_markup=kb_generation(kb_list = [
                    [KeyboardButton(text='Да')],
                    [KeyboardButton(text='Нет')]
                ]))
                await state.set_state(MiniSurvey.low_grade_state)
                await state.update_data(anon=anon)
            else:
                await db.update(tgid, 'is_complete', True, minisurvey=True)
                await db.update(tgid, 'complete_date', date.today(), minisurvey=True)
                if anon:
                    await message.answer(f'{msgs['thanks']}', reply_markup=spec_kb_generation(answrs['thanks']))
                    await state.set_state(MiniSurvey.question5)
                else:
                    await message.answer(msgs['thanks'], reply_markup=spec_kb_generation(answrs['thanks2']))
                    await state.set_state(MiniSurvey.question5)


@mini_survey_router.message(MiniSurvey.question5)
async def state5(message: Message, state: FSMContext):
    tgid = message.from_user.id
    text = message.text
    anon = '-' == await db.fetchval("SELECT contacts FROM public.mini_survey WHERE telegram_id = $1", tgid)
    await db.update(tgid, 'is_complete', True, minisurvey=True)
    await db.update(tgid, 'complete_date', date.today(), minisurvey=True)
    if text == 'До свидания':
        kb_list = [
            [KeyboardButton(text='Пройти опрос')] # TODO еще кнопка 'Оценить качество обучения'
        ]
        if is_admin(message.from_user.id):
            kb_list.append([KeyboardButton(text='Админ-панель')])
        await message.answer('Главная панель', reply_markup=kb_generation(kb_list=kb_list))
        await state.set_state(Survey.init_state)
    elif text == 'Хочу связаться с менеджером':
        if anon == False:
            await db.update(tgid, 'wants_feedback', True, minisurvey=True)
            await message.answer('Мы обязательно свяжемся с Вами', reply_markup=spec_kb_generation(answrs['thanks4']))
        else:
            await message.answer("Пожалуйста, напишите Ваше ФИО и номер телефона\n\nПример: 'Иванов Иван Иванович, 88120000000'", reply_markup=ReplyKeyboardRemove())
            await state.set_state(MiniSurvey.contax_state)
    elif text == 'Хочу оставить контактные данные':
        await message.answer("Пожалуйста, напишите Ваше ФИО и номер телефона\n\nПример: 'Иванов Иван Иванович, 88120000000'", reply_markup=ReplyKeyboardRemove())
        await state.set_state(MiniSurvey.contax_state)


@mini_survey_router.message(MiniSurvey.low_grade_state)
async def low_grade_state(message: Message, state: FSMContext):
    text = message.text
    tgid = message.from_user.id
    data = await state.get_data()
    try:
        anon = data['anon']
    except:
        anon = '-' == await db.fetchval("SELECT contacts FROM public.mini_survey WHERE telegram_id = $1", tgid) 
    if text not in ['Да', 'Нет']:
        await message.answer("Некорректный ответ", reply_markup=kb_generation(kb_list = [
                    [KeyboardButton(text='Да')],
                    [KeyboardButton(text='Нет')]
                ]))
        await state.set_state(MiniSurvey.low_grade_state)
        await state.update_data(anon=anon)
    else:
        if text == 'Нет':
            if anon:
                await message.answer(f'{msgs['thanks']}', reply_markup=spec_kb_generation(answrs['thanks2']))
            else:
                await message.answer(f'{msgs['thanks']}', reply_markup=kb_generation(kb_list=[[KeyboardButton(text='До свидания')]]))
            await state.set_state(MiniSurvey.question5)
        else:
            await db.update(tgid, 'wants_feedback', True, minisurvey=True)
            if anon:
                await message.answer("Пожалуйста, напишите Ваше ФИО и номер телефона\n\nПример: 'Иванов Иван Иванович, 88120000000'", reply_markup=ReplyKeyboardRemove())
                await state.set_state(MiniSurvey.contax_state)
            else:
                await message.answer(msgs['thanks2'], reply_markup=kb_generation(kb_list=[[KeyboardButton(text='До свидания')]]))
                await state.set_state(MiniSurvey.question5)


@mini_survey_router.message(MiniSurvey.contax_state)
async def contax_state(message: Message, state: FSMContext):
    text = message.text
    await db.update(message.from_user.id, 'contacts', text, minisurvey=True)
    await message.answer('Данные сохранены', reply_markup=spec_kb_generation(answrs['thanks4']))
    await state.set_state(MiniSurvey.question5)


@mini_survey_router.message(MiniSurvey.other_state)
async def other_state(message: Message, state: FSMContext):
    data = await state.get_data()
    active_state = data['active_state']
    questions = data['questions']
    answers = data['answers']
    current_question = data['current_question']
    text = message.text
    await db.update(message.from_user.id, current_question, text, minisurvey=True)
    await message.answer(f"{msgs[questions]}",reply_markup=spec_kb_generation(answrs[answers], next_button=False))
    await state.set_state(active_state)