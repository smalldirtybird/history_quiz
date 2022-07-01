import os
import random
import re
from collections import defaultdict


def convert_quiz_files_to_dict():
    folder = os.environ['QUIZ_FILES_PATH']
    question_files = os.listdir(folder)
    quiz_content = defaultdict(dict)
    for question_filename in question_files:
        question_filepath = os.path.join(folder, question_filename)
        with open(question_filepath, 'r', encoding='KOI8-R') as question_file:
            questions_text = question_file.read()
            text_strings = questions_text.split('\n\n')
            for text_string in text_strings:
                if ':\n' in text_string:
                    header, value = text_string.split(sep=':\n', maxsplit=1)
                    if 'Вопрос' in header:
                        question = value
                    elif 'Ответ' in header:
                        quiz_content[question] = value
    return quiz_content


def get_new_question(user_id, connection, content):
    question, answer = random.choice(list(content.items()))
    connection.set(user_id, answer)
    print(answer)
    return question


def get_correct_answer(user_id, connection):
    correct_answer = connection.get(user_id).decode('UTF-8')
    if '.' in correct_answer or '(' in correct_answer:
        correct_answer, explanation = re.split(
            '\.| \(', correct_answer, maxsplit=1)
    return correct_answer


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    print(type(convert_quiz_files_to_dict().items()))
