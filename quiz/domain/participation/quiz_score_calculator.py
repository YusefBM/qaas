from quiz.domain.quiz.question_repository import QuestionRepository
from quiz.domain.quiz.answer_repository import AnswerRepository
from quiz.domain.quiz.invalid_question_for_quiz_exception import InvalidQuestionForQuizException
from quiz.domain.quiz.invalid_answer_for_question_exception import InvalidAnswerForQuestionException
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.answer import Answer
from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException
from quiz.domain.participation.quiz_score_result import QuizScoreResult, SubmittedAnswer


class QuizScoreCalculator:

    def __init__(
        self,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
    ) -> None:
        self.__question_repository = question_repository
        self.__answer_repository = answer_repository

    def calculate(
        self, quiz: Quiz, participation: Participation, submitted_answers: list[SubmittedAnswer]
    ) -> QuizScoreResult:
        self.__validate_no_duplicate_submissions(submitted_answers)

        questions_by_id, answers_by_id = self.__fetch_quiz_data(submitted_answers)
        answer_submissions = self.__create_answer_submissions(
            submitted_answers, questions_by_id, answers_by_id, quiz, participation
        )

        return self.__calculate_final_score(answer_submissions)

    def __validate_no_duplicate_submissions(self, submitted_answers: list[SubmittedAnswer]) -> None:
        answered_question_ids = set()

        for current_submission in submitted_answers:
            if current_submission.question_id in answered_question_ids:
                raise DuplicateAnswerSubmissionException(question_id=current_submission.question_id)
            answered_question_ids.add(current_submission.question_id)

    def __fetch_quiz_data(
        self, submitted_answers: list[SubmittedAnswer]
    ) -> tuple[dict[int, Question], dict[int, Answer]]:
        question_ids = [submission.question_id for submission in submitted_answers]
        answer_ids = [submission.answer_id for submission in submitted_answers]

        questions_by_id = self.__question_repository.find_by_ids(question_ids)
        answers_by_id = self.__answer_repository.find_by_ids(answer_ids)

        return questions_by_id, answers_by_id

    def __create_answer_submissions(
        self,
        submitted_answers: list[SubmittedAnswer],
        questions_by_id: dict[int, Question],
        answers_by_id: dict[int, Answer],
        quiz: Quiz,
        participation: Participation,
    ) -> list[AnswerSubmission]:
        answer_submissions = []

        for current_submission in submitted_answers:
            question = questions_by_id.get(current_submission.question_id)
            self.__validate_question_belongs_to_quiz(question, quiz, current_submission.question_id)

            answer = answers_by_id.get(current_submission.answer_id)
            self.__validate_answer_belongs_to_question(
                answer, question, current_submission.answer_id, current_submission.question_id
            )

            answer_submission = AnswerSubmission(
                participation=participation,
                question=question,
                selected_answer=answer,
            )
            answer_submissions.append(answer_submission)

        return answer_submissions

    def __validate_question_belongs_to_quiz(self, question: Question, quiz: Quiz, question_id: int) -> None:
        if question is None or question.quiz_id != quiz.id:
            raise InvalidQuestionForQuizException(question_id=question_id, quiz_id=quiz.id)

    def __validate_answer_belongs_to_question(
        self, answer: Answer, question: Question, answer_id: int, question_id: int
    ) -> None:
        if answer is None or answer.question_id != question.id:
            raise InvalidAnswerForQuestionException(answer_id=answer_id, question_id=question_id)

    def __calculate_final_score(self, answer_submissions: list[AnswerSubmission]) -> QuizScoreResult:
        total_score = 0
        total_possible_score = 0

        for submission in answer_submissions:
            total_possible_score += submission.question.points

        for submission in answer_submissions:
            if submission.is_correct:
                total_score += submission.question.points

        return QuizScoreResult(
            total_score=total_score, total_possible_score=total_possible_score, answer_submissions=answer_submissions
        )
