import json


def load_messages():
    with open('/home/geneticisst/feedback_tg_wsl_bot/messages.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def load_answers():
    with open('/home/geneticisst/feedback_tg_wsl_bot/answers.json', 'r', encoding='utf-8') as file:
        return json.load(file)


msgs = load_messages()
answrs = load_answers()