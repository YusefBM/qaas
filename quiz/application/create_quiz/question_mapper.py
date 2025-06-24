from quiz.application.create_quiz.answer_data import AnswerData
from quiz.application.create_quiz.question_data import QuestionData
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.quiz import Quiz


class QuestionMapper:
    def map_to_domain(self, quiz: Quiz, question_data: QuestionData) -> tuple[Question, list[Answer]]:
        question = Question(
            quiz=quiz,
            text=question_data["text"],
            order=question_data["order"],
            points=question_data["points"],
        )
        answers = [self.__map_to_answer(question, answer) for answer in question_data["answers"]]
        return question, answers

    def __map_to_answer(self, question: Question, answer_data: AnswerData) -> Answer:
        return Answer(
            question=question,
            text=answer_data["text"],
            order=answer_data["order"],
            is_correct=answer_data["is_correct"],
        )
