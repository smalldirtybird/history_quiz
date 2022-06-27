import os
from collections import defaultdict


def convert_quiz_files_to_dict(folder):
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
