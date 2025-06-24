from uuid import UUID


class ParticipationNotFoundException(Exception):
    def __init__(self, participation_id: UUID):
        self.participation_id = participation_id
        super().__init__(f"Participation {participation_id} not found. User must accept the invitation first")
