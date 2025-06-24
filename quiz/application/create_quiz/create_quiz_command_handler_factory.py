from user.infrastructure.db_user_repository import DbUserRepository
from .create_quiz_command_handler import CreateQuizCommandHandler
from .question_mapper import QuestionMapper
from ...domain.quiz.question_validator import QuestionValidator
from ...infrastructure.db_answer_repository import DbAnswerRepository
from ...infrastructure.db_question_repository import DbQuestionRepository
from ...infrastructure.db_quiz_repository import DbQuizRepository


class CreateQuizCommandHandlerFactory:
    @staticmethod
    def create() -> CreateQuizCommandHandler:
        return CreateQuizCommandHandler(
            user_repository=DbUserRepository(),
            quiz_repository=DbQuizRepository(),
            question_repository=DbQuestionRepository(),
            answer_repository=DbAnswerRepository(),
            question_mapper=QuestionMapper(),
            question_validator=QuestionValidator(),
        )
