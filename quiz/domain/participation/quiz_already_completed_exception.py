from uuid import UUID


class QuizAlreadyCompletedException(Exception):
    def __init__(self, quiz_id: UUID):
        self.quiz_id = quiz_id
        super().__init__(f"Quiz {self.quiz_id} has already been completed.")
