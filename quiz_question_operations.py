import json
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


def get_clear_answer(answer):
    if '.' in answer or '(' in answer:
        answer, explanation = re.split(
            r'\.| \(', answer, maxsplit=1)
    return answer
