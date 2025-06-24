from uuid import UUID


class InvalidQuestionForQuizException(Exception):
    def __init__(self, question_id: int, quiz_id: UUID):
        self.question_id = question_id
        self.quiz_id = quiz_id
        self.message = f"Question '{question_id}' does not belong to quiz '{quiz_id}'"
        super().__init__(self.message)
