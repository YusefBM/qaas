class AnswerAlreadyExistsException(Exception):
    def __init__(self, order: int, question_id: int) -> None:
        self.order = order
        self.question_id = question_id
        super().__init__(f"Answer with order '{self.order}' already exists for the question '{question_id}'")
