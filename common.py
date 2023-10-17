from pathlib import Path
import re


def extract_questions(text) -> dict:
    questions = re.findall(r'Вопрос \d+:\s(.*?)Ответ', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.+)\.\s\s', text)
    return dict(zip(questions, answers))


def get_questions(quiz_folder) -> dict:
    questions = {}
    for file_name in Path(quiz_folder).iterdir():
        path = Path.cwd() / file_name
        text = path.read_text(encoding='KOI8-R')
        questions.update(extract_questions(text))
        break
    return questions


def check_answer(user_answer, correct_answer):
    user_answer = user_answer.strip()
    correct_answer = re.sub(r'[\(\[][^()]*[\)\]]', '', correct_answer)
    correct_answer = correct_answer.strip()
    if '"' in correct_answer:
        correct_answer = correct_answer.replace('"', '')
    if '... ' in correct_answer:
        correct_answer = correct_answer.replace('... ', '')
    if user_answer == correct_answer:
        return True
    return False
