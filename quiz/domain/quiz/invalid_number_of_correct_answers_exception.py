class InvalidNumberOfCorrectAnswersException(Exception):
    def __init__(self, quiz_id: str) -> None:
        self.quiz_id = quiz_id
        super().__init__(f"Every question from quiz '{self.quiz_id}' must have only one correct answer")
