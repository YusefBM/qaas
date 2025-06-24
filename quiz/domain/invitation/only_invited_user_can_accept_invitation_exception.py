from uuid import UUID


class OnlyInvitedUserCanAcceptInvitationException(Exception):
    def __init__(self, invitation_id: UUID, user_id: UUID):
        self.invitation_id = invitation_id
        self.user_id = user_id
        super().__init__(f"User {user_id} is not authorized to accept invitation {invitation_id}")
