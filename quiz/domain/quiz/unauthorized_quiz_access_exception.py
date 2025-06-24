class UnauthorizedQuizAccessException(Exception):
    def __init__(self, quiz_id: str, user_id: str):
        self.quiz_id = quiz_id
        self.user_id = user_id
        super().__init__(f"User '{user_id}' is not authorized to access quiz '{quiz_id}'")
