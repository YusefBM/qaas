from uuid import UUID


class ParticipationNotFoundForQuizAndParticipantException(Exception):
    def __init__(self, quiz_id: UUID, participant_id: UUID):
        self.quiz_id = quiz_id
        self.participant_id = participant_id
        super().__init__(f"Participation not found for quiz {quiz_id} and participant {participant_id}")
