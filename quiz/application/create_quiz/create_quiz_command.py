from dataclasses import dataclass

from quiz.application.create_quiz.question_data import QuestionData


@dataclass(frozen=True)
class CreateQuizCommand:
    title: str
    description: str
    creator_id: str
    questions: list[QuestionData]
