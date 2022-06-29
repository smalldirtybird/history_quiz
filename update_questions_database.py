import argparse
import json
import os
import re
from collections import defaultdict

import redis
from dotenv import load_dotenv


def upload_questions_to_database(folder, connection):
    question_files = os.listdir(folder)
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
                        question_id = f'question_{count}'
                        question_content = defaultdict(dict)
                        question_content['question'] = value
                    elif 'Ответ' in header:
                        value = value.replace('... ', '')
                        if '.' in value or '(' in value:
                            answer, explanation = re.split(
                                '\.| \(', value, maxsplit=1)
                            question_content['answer'] = answer
                        else:
                            question_content['answer'] = value
                        value_string = json.dumps(
                            question_content, ensure_ascii=False)
                        connection.set(question_id, value_string)


def get_folder_path_argument():
    parser = argparse.ArgumentParser(
        description='Update questions database for history quiz bot.')
    parser.add_argument(
        '-dir', '--directory', default='quiz_questions',
        help='Path to folder with questions files.')
    args = parser.parse_args()
    return args.directory


if __name__ == '__main__':
    load_dotenv()
    redis_connection = redis.Redis(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        password=os.environ['DB_PASSWORD']
        )
    keys = redis_connection.keys()
    for key in keys:
        if 'question_' in key.decode('UTF-8'):
            redis_connection.delete(key)
    quiz_questions_folder_path = get_folder_path_argument()
    upload_questions_to_database(
        quiz_questions_folder_path, redis_connection)
