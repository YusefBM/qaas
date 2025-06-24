from uuid import UUID

from quiz.application.get_quiz_query.get_quiz_query import GetQuizQuery


class GetQuizQueryValidationError(Exception):
    """Exception raised when query validation fails"""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field
        self.message = message


class GetQuizQueryValidator:
    """Validator for GetQuizQuery input parameters"""

    @staticmethod
    def validate(query: GetQuizQuery) -> None:
        """
        Validate query parameters

        Raises:
            GetQuizQueryValidationError: If validation fails
        """
        if query is None:
            raise GetQuizQueryValidationError("Query cannot be None")

        GetQuizQueryValidator._validate_quiz_id(query.quiz_id)
        GetQuizQueryValidator._validate_participant_id(query.participant_id)

    @staticmethod
    def _validate_quiz_id(quiz_id: UUID) -> None:
        """Validate quiz ID parameter"""
        if quiz_id is None:
            raise GetQuizQueryValidationError("Quiz ID cannot be None", "quiz_id")

        if not isinstance(quiz_id, UUID):
            raise GetQuizQueryValidationError("Quiz ID must be a valid UUID", "quiz_id")

    @staticmethod
    def _validate_participant_id(participant_id: UUID) -> None:
        """Validate participant ID parameter"""
        if participant_id is None:
            raise GetQuizQueryValidationError("Participant ID cannot be None", "participant_id")

        if not isinstance(participant_id, UUID):
            raise GetQuizQueryValidationError("Participant ID must be a valid UUID", "participant_id")
