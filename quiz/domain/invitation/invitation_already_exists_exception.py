class InvitationAlreadyExistsException(Exception):
    def __init__(self, quiz_id: str, participant_id: str):
        self.quiz_id = quiz_id
        self.participant_id = participant_id
        super().__init__(f"Invitation already exists for participant '{participant_id}' in quiz '{quiz_id}'")
