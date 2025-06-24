from uuid import UUID

from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_data import QuizData, QuestionData, AnswerData
from quiz.domain.quiz.quiz_finder import QuizFinder
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException


class DbQuizFinder(QuizFinder):
    def find_quiz_for_participation(self, quiz_id: UUID, participant_id: UUID) -> QuizData:
        try:
            quiz = Quiz.objects.prefetch_related("questions__answers").get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise QuizNotFoundException(quiz_id=str(quiz_id))

        questions = self._build_questions_from_quiz(quiz)

        return QuizData(
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            quiz_description=quiz.description,
            quiz_creator_id=quiz.creator_id,
            questions=questions,
        )

    def _build_questions_from_quiz(self, quiz: Quiz) -> list[QuestionData]:
        questions = []

        for question in quiz.questions.all().order_by("order"):
            answers = []
            for answer in question.answers.all().order_by("order"):
                answers.append(
                    AnswerData(
                        answer_id=answer.id,
                        text=answer.text,
                        order=answer.order,
                    )
                )

            questions.append(
                QuestionData(
                    question_id=question.id,
                    text=question.text,
                    order=question.order,
                    points=question.points,
                    answers=answers,
                )
            )

        return questions
