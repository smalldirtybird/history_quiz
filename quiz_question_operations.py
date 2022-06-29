import json
import os
import random
from collections import defaultdict


def convert_quiz_files_to_dict():
    folder = os.environ['QUIZ_FILES_PATH']
    question_files = os.listdir(folder)
    quiz_content = defaultdict(dict)
    count = 0
    for question_filename in question_files:
        question_filepath = os.path.join(folder, question_filename)
        with open(question_filepath, 'r', encoding='KOI8-R') as question_file:
            questions_text = question_file.read()
            text_strings = questions_text.split('\n\n')
            for text_string in text_strings:
                if ':\n' in text_string:
                    header, value = text_string.split(sep=':\n', maxsplit=1)
                    if 'Вопрос' in header:
                        count += 1
                        quiz_content[str(count)]['question'] = value
                    elif 'Ответ' in header:
                        quiz_content[str(count)]['answer'] = value
    return quiz_content


def get_new_question(db_user_id, connection):
    question_number = str(random.randint(
        1, len(connection.keys('question_*'))))
    question_id = f'question_{question_number}'
    db_user_info = json.dumps({'last_asked_question': question_id})
    connection.set(db_user_id, db_user_info)
    quiz_question = json.loads(connection.get(question_id))['question']
    return quiz_question


def get_correct_answer(db_user_id, connection):
    db_user_info = json.loads(connection.get(db_user_id).decode('UTF-8'))
    question_id = db_user_info['last_asked_question']
    question_content = json.loads(connection.get(question_id).decode('UTF-8'))
    correct_answer = question_content['answer']
    return correct_answer
