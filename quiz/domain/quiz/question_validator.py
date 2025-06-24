from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.invalid_number_of_answers_exception import InvalidNumberOfAnswersException
from quiz.domain.quiz.invalid_number_of_correct_answers_exception import InvalidNumberOfCorrectAnswersException
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_validator_context import QuestionValidatorContext


class QuestionValidator:
    def validate(self, context: QuestionValidatorContext) -> None:
        if len(context.answers) != Question.REQUIRED_NUMBER_OF_ANSWERS:
            raise InvalidNumberOfAnswersException(quiz_id=context.question.quiz_id)

        if len(self.__get_correct_answers(context.answers)) != 1:
            raise InvalidNumberOfCorrectAnswersException(quiz_id=context.question.quiz_id)

    def __get_correct_answers(self, answers: list[Answer]) -> list[Answer]:
        return [answer for answer in answers if answer.is_correct]
