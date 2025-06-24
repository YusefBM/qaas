class QuizNotFoundException(Exception):
    def __init__(self, quiz_id: str):
        self.quiz_id = quiz_id
        super().__init__(f"Quiz with ID '{quiz_id}' not found")
