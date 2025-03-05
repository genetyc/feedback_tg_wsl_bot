import json


def load_messages():
    with open('messages.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def load_answers():
    with open('answers.json', 'r', encoding='utf-8') as file:
        return json.load(file)


msgs = load_messages()
answrs = load_answers()