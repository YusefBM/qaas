from quiz.domain.participation.quiz_score_calculator import QuizScoreCalculator
from quiz.infrastructure.db_question_repository import DbQuestionRepository
from quiz.infrastructure.db_answer_repository import DbAnswerRepository


class QuizScoreCalculatorFactory:
    @staticmethod
    def create() -> QuizScoreCalculator:
        return QuizScoreCalculator(
            question_repository=DbQuestionRepository(),
            answer_repository=DbAnswerRepository(),
        )
