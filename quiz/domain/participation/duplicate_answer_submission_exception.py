class DuplicateAnswerSubmissionException(Exception):
    def __init__(self, question_id: int):
        self.question_id = question_id
        self.message = (
            f"Multiple answers provided for question '{question_id}'. Each question can only be answered once."
        )
        super().__init__(self.message)
