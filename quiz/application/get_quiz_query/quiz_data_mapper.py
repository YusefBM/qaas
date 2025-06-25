from quiz.application.get_quiz_query.get_quiz_query_response import (
    GetQuizQueryResponse,
    QuizQuestion,
    QuizAnswer,
)
from quiz.domain.quiz.quiz_data import QuizData, AnswerData, QuestionData


class QuizDataMapper:
    def map_to_response(self, quiz_data: QuizData) -> GetQuizQueryResponse:
        questions = self.__map_questions(quiz_data.questions)

        return GetQuizQueryResponse(
            quiz_id=quiz_data.quiz_id,
            title=quiz_data.quiz_title,
            description=quiz_data.quiz_description,
            questions=questions,
        )

    def __map_questions(self, questions: list[QuestionData]) -> list[QuizQuestion]:
        return [
            QuizQuestion(
                question_id=question_data.question_id,
                text=question_data.text,
                order=question_data.order,
                answers=self.__map_answers(question_data.answers),
            )
            for question_data in questions
        ]

    def __map_answers(self, answers: list[AnswerData]) -> list[QuizAnswer]:
        return [
            QuizAnswer(
                answer_id=answer_data.answer_id,
                text=answer_data.text,
                order=answer_data.order,
            )
            for answer_data in answers
        ]
