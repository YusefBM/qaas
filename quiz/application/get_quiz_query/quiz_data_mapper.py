from typing import List

from quiz.application.get_quiz_query.get_quiz_query_response import (
    GetQuizQueryResponse,
    QuizQuestion,
    QuizAnswer,
)
from quiz.domain.quiz.quiz_data import QuizData


class QuizDataMapper:

    @staticmethod
    def map_to_response(quiz_data: QuizData) -> GetQuizQueryResponse:
        questions = QuizDataMapper._map_questions(quiz_data)

        return GetQuizQueryResponse(
            quiz_id=quiz_data.quiz_id,
            title=quiz_data.quiz_title,
            description=quiz_data.quiz_description,
            questions=questions,
        )

    @staticmethod
    def _map_questions(quiz_data: QuizData) -> List[QuizQuestion]:
        return [
            QuizQuestion(
                question_id=question_data.question_id,
                text=question_data.text,
                order=question_data.order,
                answers=QuizDataMapper._map_answers(question_data.answers),
            )
            for question_data in quiz_data.questions
        ]

    @staticmethod
    def _map_answers(answers) -> List[QuizAnswer]:
        return [
            QuizAnswer(
                answer_id=answer_data.answer_id,
                text=answer_data.text,
                order=answer_data.order,
            )
            for answer_data in answers
        ]
