from logging import getLogger

from django.db import transaction

from quiz.application.submit_quiz_answers.submit_quiz_answers_command import SubmitQuizAnswersCommand
from quiz.application.submit_quiz_answers.submit_quiz_answers_response import SubmitQuizAnswersResponse
from quiz.domain.participation.answer_submission_repository import AnswerSubmissionRepository
from quiz.domain.participation.incomplete_quiz_submission_exception import IncompleteQuizSubmissionException
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.participation.quiz_already_completed_exception import QuizAlreadyCompletedException
from quiz.domain.participation.quiz_score_calculator import QuizScoreCalculator, SubmittedAnswer
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user_repository import UserRepository


class SubmitQuizAnswersCommandHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        participation_repository: ParticipationRepository,
        answer_submission_repository: AnswerSubmissionRepository,
        quiz_score_calculator: QuizScoreCalculator,
        user_repository: UserRepository,
    ) -> None:
        self.__quiz_repository = quiz_repository
        self.__participation_repository = participation_repository
        self.__answer_submission_repository = answer_submission_repository
        self.__quiz_score_calculator = quiz_score_calculator
        self.__user_repository = user_repository
        self.__logger = getLogger(__name__)

    def handle(self, command: SubmitQuizAnswersCommand) -> SubmitQuizAnswersResponse:
        self.__logger.info(
            f"Submitting quiz answers for quiz '{command.quiz_id}' by participant '{command.participant_id}'"
        )

        quiz = self.__quiz_repository.find_or_fail_by_id(command.quiz_id)
        participant = self.__user_repository.find_or_fail_by_id(command.participant_id)

        participation = self.__participation_repository.find_or_fail_by_quiz_and_participant(quiz, participant)

        if participation.is_completed():
            raise QuizAlreadyCompletedException(quiz_id=command.quiz_id)

        if len(command.answers) != quiz.total_questions:
            raise IncompleteQuizSubmissionException(
                expected_answers=quiz.total_questions,
                received_answers=len(command.answers),
            )

        submitted_answers = [SubmittedAnswer(answer.question_id, answer.answer_id) for answer in command.answers]

        quiz_score_result = self.__quiz_score_calculator.calculate(
            quiz=quiz, participation=participation, submitted_answers=submitted_answers
        )

        participation.complete(score=quiz_score_result.total_score)

        with transaction.atomic():
            self.__answer_submission_repository.bulk_save(quiz_score_result.answer_submissions)
            self.__participation_repository.save(participation)

        self.__logger.info(
            f"Quiz '{command.quiz_id}' completed by participant '{command.participant_id}' with score {quiz_score_result.total_score}"
        )

        return SubmitQuizAnswersResponse(
            message="Quiz completed successfully",
            participation_id=participation.id,
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            score=quiz_score_result.total_score,
            total_possible_score=quiz_score_result.total_possible_score,
            completed_at=participation.get_formatted_completed_at(),
        )
