class QuestionAlreadyExistsException(Exception):
    def __init__(self, order: int, quiz_id: str) -> None:
        self.order = order
        self.quiz_id = quiz_id
        super().__init__(f"Question with order '{self.order}' already exists for the quiz '{quiz_id}'")
