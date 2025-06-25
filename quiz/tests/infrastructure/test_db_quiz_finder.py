import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_data import QuizData
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.db_quiz_finder import DbQuizFinder


class TestDbQuizFinder(unittest.TestCase):
    def setUp(self):
        self.finder = DbQuizFinder()
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.participant_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.creator_id = UUID("11111111-2222-3333-4444-555555555555")

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_success_with_questions_and_answers(self, mock_objects):
        mock_answer1 = Mock(spec=Answer)
        mock_answer1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        mock_answer1.text = "JavaScript"
        mock_answer1.order = 1

        mock_answer2 = Mock(spec=Answer)
        mock_answer2.id = UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff")
        mock_answer2.text = "Python"
        mock_answer2.order = 2

        mock_answer3 = Mock(spec=Answer)
        mock_answer3.id = UUID("cccccccc-dddd-eeee-ffff-000000000000")
        mock_answer3.text = "True"
        mock_answer3.order = 1

        mock_answer4 = Mock(spec=Answer)
        mock_answer4.id = UUID("dddddddd-eeee-ffff-0000-111111111111")
        mock_answer4.text = "False"
        mock_answer4.order = 2

        mock_answers_queryset1 = Mock()
        mock_answers_queryset1.all.return_value.order_by.return_value = [mock_answer1, mock_answer2]

        mock_answers_queryset2 = Mock()
        mock_answers_queryset2.all.return_value.order_by.return_value = [mock_answer3, mock_answer4]

        mock_question1 = Mock(spec=Question)
        mock_question1.id = UUID("eeeeeeee-ffff-0000-1111-222222222222")
        mock_question1.text = "What is your favorite programming language?"
        mock_question1.order = 1
        mock_question1.points = 10
        mock_question1.answers = mock_answers_queryset1

        mock_question2 = Mock(spec=Question)
        mock_question2.id = UUID("ffffffff-0000-1111-2222-333333333333")
        mock_question2.text = "Is JavaScript interpreted?"
        mock_question2.order = 2
        mock_question2.points = 5
        mock_question2.answers = mock_answers_queryset2

        mock_questions_queryset = Mock()
        mock_questions_queryset.all.return_value.order_by.return_value = [mock_question1, mock_question2]

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Programming Quiz"
        mock_quiz.description = "Test your programming knowledge"
        mock_quiz.creator_id = self.creator_id
        mock_quiz.questions = mock_questions_queryset

        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.return_value = mock_quiz
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        result = self.finder.find_quiz_for_participation(self.quiz_id, self.participant_id)

        self.assertIsInstance(result, QuizData)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Programming Quiz")
        self.assertEqual(result.quiz_description, "Test your programming knowledge")
        self.assertEqual(result.quiz_creator_id, self.creator_id)
        self.assertEqual(len(result.questions), 2)

        question1 = result.questions[0]
        self.assertEqual(question1.question_id, UUID("eeeeeeee-ffff-0000-1111-222222222222"))
        self.assertEqual(question1.text, "What is your favorite programming language?")
        self.assertEqual(question1.order, 1)
        self.assertEqual(question1.points, 10)
        self.assertEqual(len(question1.answers), 2)

        answer1 = question1.answers[0]
        self.assertEqual(answer1.answer_id, UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"))
        self.assertEqual(answer1.text, "JavaScript")
        self.assertEqual(answer1.order, 1)

        question2 = result.questions[1]
        self.assertEqual(question2.question_id, UUID("ffffffff-0000-1111-2222-333333333333"))
        self.assertEqual(question2.text, "Is JavaScript interpreted?")
        self.assertEqual(question2.order, 2)
        self.assertEqual(question2.points, 5)
        self.assertEqual(len(question2.answers), 2)

        mock_objects.prefetch_related.assert_called_once_with("questions__answers")
        mock_prefetch_queryset.get.assert_called_once_with(id=self.quiz_id)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_success_with_empty_quiz(self, mock_objects):
        mock_questions_queryset = Mock()
        mock_questions_queryset.all.return_value.order_by.return_value = []

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Empty Quiz"
        mock_quiz.description = "Quiz without questions"
        mock_quiz.creator_id = self.creator_id
        mock_quiz.questions = mock_questions_queryset

        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.return_value = mock_quiz
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        result = self.finder.find_quiz_for_participation(self.quiz_id, self.participant_id)

        self.assertIsInstance(result, QuizData)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Empty Quiz")
        self.assertEqual(result.quiz_description, "Quiz without questions")
        self.assertEqual(result.quiz_creator_id, self.creator_id)
        self.assertEqual(len(result.questions), 0)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_success_with_questions_without_answers(self, mock_objects):
        mock_answers_queryset = Mock()
        mock_answers_queryset.all.return_value.order_by.return_value = []

        mock_question = Mock(spec=Question)
        mock_question.id = UUID("eeeeeeee-ffff-0000-1111-222222222222")
        mock_question.text = "Question without answers"
        mock_question.order = 1
        mock_question.points = 5
        mock_question.answers = mock_answers_queryset

        mock_questions_queryset = Mock()
        mock_questions_queryset.all.return_value.order_by.return_value = [mock_question]

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Quiz with Unanswered Questions"
        mock_quiz.description = "Questions without answers"
        mock_quiz.creator_id = self.creator_id
        mock_quiz.questions = mock_questions_queryset

        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.return_value = mock_quiz
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        result = self.finder.find_quiz_for_participation(self.quiz_id, self.participant_id)

        self.assertIsInstance(result, QuizData)
        self.assertEqual(len(result.questions), 1)
        self.assertEqual(len(result.questions[0].answers), 0)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_raises_quiz_not_found_exception(self, mock_objects):
        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.side_effect = Quiz.DoesNotExist
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        with self.assertRaises(QuizNotFoundException) as context:
            self.finder.find_quiz_for_participation(self.quiz_id, self.participant_id)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_different_quiz_id(self, mock_objects):
        different_quiz_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        mock_questions_queryset = Mock()
        mock_questions_queryset.all.return_value.order_by.return_value = []

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = different_quiz_id
        mock_quiz.title = "Different Quiz"
        mock_quiz.description = "A different quiz"
        mock_quiz.creator_id = self.creator_id
        mock_quiz.questions = mock_questions_queryset

        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.return_value = mock_quiz
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        result = self.finder.find_quiz_for_participation(different_quiz_id, self.participant_id)

        self.assertEqual(result.quiz_id, different_quiz_id)
        self.assertEqual(result.quiz_title, "Different Quiz")
        mock_prefetch_queryset.get.assert_called_once_with(id=different_quiz_id)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_quiz_for_participation_with_single_question_and_answer(self, mock_objects):
        mock_answer = Mock(spec=Answer)
        mock_answer.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        mock_answer.text = "Single Answer"
        mock_answer.order = 1

        mock_answers_queryset = Mock()
        mock_answers_queryset.all.return_value.order_by.return_value = [mock_answer]

        mock_question = Mock(spec=Question)
        mock_question.id = UUID("eeeeeeee-ffff-0000-1111-222222222222")
        mock_question.text = "Single Question"
        mock_question.order = 1
        mock_question.points = 15
        mock_question.answers = mock_answers_queryset

        mock_questions_queryset = Mock()
        mock_questions_queryset.all.return_value.order_by.return_value = [mock_question]

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Single Question Quiz"
        mock_quiz.description = "Quiz with one question"
        mock_quiz.creator_id = self.creator_id
        mock_quiz.questions = mock_questions_queryset

        mock_prefetch_queryset = Mock()
        mock_prefetch_queryset.get.return_value = mock_quiz
        mock_objects.prefetch_related.return_value = mock_prefetch_queryset

        result = self.finder.find_quiz_for_participation(self.quiz_id, self.participant_id)

        self.assertEqual(len(result.questions), 1)
        self.assertEqual(len(result.questions[0].answers), 1)
        self.assertEqual(result.questions[0].answers[0].text, "Single Answer")
