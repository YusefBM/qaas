from typing import TypedDict


class AnswerData(TypedDict):
    text: str
    order: int
    is_correct: bool
