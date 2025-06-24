from dataclasses import dataclass


@dataclass(frozen=True)
class CreateQuizResponse:
    quiz_id: str

    def as_dict(self) -> dict:
        return {"id": self.quiz_id}
