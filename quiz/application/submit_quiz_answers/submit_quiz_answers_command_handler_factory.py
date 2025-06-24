from quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler import SubmitQuizAnswersCommandHandler
from quiz.domain.participation.quiz_score_calculator_factory import QuizScoreCalculatorFactory
from quiz.infrastructure.db_answer_submission_repository import DbAnswerSubmissionRepository
from quiz.infrastructure.db_participation_repository import DbParticipationRepository
from quiz.infrastructure.db_quiz_repository import DbQuizRepository
from user.infrastructure.db_user_repository import DbUserRepository


class SubmitQuizAnswersCommandHandlerFactory:
    @staticmethod
    def create() -> SubmitQuizAnswersCommandHandler:
        return SubmitQuizAnswersCommandHandler(
            quiz_repository=DbQuizRepository(),
            participation_repository=DbParticipationRepository(),
            answer_submission_repository=DbAnswerSubmissionRepository(),
            quiz_score_calculator=QuizScoreCalculatorFactory.create(),
            user_repository=DbUserRepository(),
        )
