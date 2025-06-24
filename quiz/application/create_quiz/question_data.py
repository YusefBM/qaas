from typing import TypedDict

from quiz.application.create_quiz.answer_data import AnswerData


class QuestionData(TypedDict):
    text: str
    order: int
    points: int
    answers: list[AnswerData]
