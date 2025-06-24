from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SubmittedAnswer:
    question_id: int
    answer_id: int


@dataclass(frozen=True)
class SubmitQuizAnswersCommand:
    participant_id: UUID
    quiz_id: UUID
    answers: list[SubmittedAnswer]
