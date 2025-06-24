from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AnswerData:
    answer_id: UUID
    text: str
    order: int


@dataclass(frozen=True)
class QuestionData:
    question_id: UUID
    text: str
    order: int
    points: int
    answers: list[AnswerData]


@dataclass(frozen=True)
class QuizData:
    quiz_id: UUID
    quiz_title: str
    quiz_description: str
    quiz_creator_id: UUID
    questions: list[QuestionData]
