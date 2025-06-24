from uuid import UUID


class OnlyQuizCreatorCanSendInvitationException(Exception):
    def __init__(self, quiz_id: UUID, user_id: UUID):
        self.quiz_id = quiz_id
        self.user_id = user_id
        super().__init__(
            f"User {user_id} is not authorized to send invitation for quiz {quiz_id} because it's not the creator"
        )
