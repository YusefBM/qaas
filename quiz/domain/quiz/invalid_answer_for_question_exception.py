class InvalidAnswerForQuestionException(Exception):
    def __init__(self, answer_id: int, question_id: int):
        self.answer_id = answer_id
        self.question_id = question_id
        self.message = f"Answer '{answer_id}' does not belong to question '{question_id}'"
        super().__init__(self.message)
