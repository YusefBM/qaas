class ParticipationNotFoundForUserException(Exception):
    def __init__(self, quiz_id: str, user_id: str):
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.message = (
            f"User '{user_id}' does not have access to quiz '{quiz_id}'. User must be invited to participate."
        )
        super().__init__(self.message)
