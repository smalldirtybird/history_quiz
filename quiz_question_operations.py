import os
import random
import re
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
                    # print(question_filepath, '\n', text_string)
                    header, value = text_string.split(sep=':\n', maxsplit=1)
                    if 'Вопрос' in header:
                        count += 1
                        quiz_content[str(count)]['question'] = value
                    elif 'Ответ' in header:
                        quiz_content[str(count)]['answer'] = value
    return quiz_content


def get_new_question(database_id, connection):
    quiz_questions = convert_quiz_files_to_dict()
    question_number = str(random.randint(1, len(quiz_questions)))
    quiz_question = quiz_questions[question_number]['question']
    connection.set(database_id, question_number)
    print(quiz_questions[question_number]['answer'])
    return quiz_question


def get_correct_answer(database_id, connection):
    quiz_questions = convert_quiz_files_to_dict()
    question_number = connection.get(database_id).decode('UTF-8')
    correct_answer = quiz_questions[question_number]['answer']
    if '.' in correct_answer or '(' in correct_answer:
        answer, explanation = re.split('\.| \(', correct_answer, maxsplit=1)
        return answer
    else:
        return correct_answer
