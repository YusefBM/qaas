from uuid import UUID


class CreatorCannotBeInvitedException(Exception):
    def __init__(self, quiz_id: UUID, creator_id: UUID):
        self.quiz_id = quiz_id
        self.creator = creator_id
        super().__init__(f"User {creator_id} cannot be invited for quiz {quiz_id} because it's the creator")
