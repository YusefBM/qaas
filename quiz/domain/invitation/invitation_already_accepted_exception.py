from uuid import UUID


class InvitationAlreadyAcceptedException(Exception):
    def __init__(self, invitation_id: UUID):
        self.invitation_id = invitation_id
        super().__init__(f"Invitation with ID {invitation_id} has already been accepted")
