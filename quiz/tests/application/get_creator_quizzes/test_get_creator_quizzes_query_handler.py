import unittest
from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_creator_quizzes.get_creator_quizzes_query import GetCreatorQuizzesQuery
from quiz.application.get_creator_quizzes.get_creator_quizzes_query_handler import GetCreatorQuizzesQueryHandler
from quiz.application.get_creator_quizzes.get_creator_quizzes_response import GetCreatorQuizzesResponse
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_repository import QuizRepository


class TestGetCreatorQuizzesQueryHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.handler = GetCreatorQuizzesQueryHandler(quiz_repository=self.quiz_repository_mock)

        self.creator_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.query = GetCreatorQuizzesQuery(creator_id=str(self.creator_id))

    def test_handle_success_with_multiple_quizzes(self):
        quiz1 = Mock(spec=Quiz)
        quiz1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        quiz1.title = "JavaScript Basics"
        quiz1.description = "Test your JavaScript knowledge"
        quiz1.total_questions = 10
        quiz1.total_participants = 25
        quiz1.created_at = datetime(2023, 1, 15, 10, 30, 0, 123456)
        quiz1.updated_at = datetime(2023, 1, 16, 14, 45, 0, 654321)
        quiz1.get_formatted_created_at.return_value = "2023-01-15T10:30:00.123456Z"
        quiz1.get_formatted_updated_at.return_value = "2023-01-16T14:45:00.654321Z"

        quiz2 = Mock(spec=Quiz)
        quiz2.id = UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff")
        quiz2.title = "Python Advanced"
        quiz2.description = "Advanced Python concepts"
        quiz2.total_questions = 15
        quiz2.total_participants = 40
        quiz2.created_at = datetime(2023, 2, 20, 8, 15, 0, 987654)
        quiz2.updated_at = datetime(2023, 2, 21, 16, 30, 0, 456789)
        quiz2.get_formatted_created_at.return_value = "2023-02-20T08:15:00.987654Z"
        quiz2.get_formatted_updated_at.return_value = "2023-02-21T16:30:00.456789Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz1, quiz2]

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetCreatorQuizzesResponse)
        self.assertEqual(result.creator_id, str(self.creator_id))
        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.quizzes), 2)

        quiz_summary1 = result.quizzes[0]
        self.assertEqual(quiz_summary1.id, quiz1.id)
        self.assertEqual(quiz_summary1.title, "JavaScript Basics")
        self.assertEqual(quiz_summary1.description, "Test your JavaScript knowledge")
        self.assertEqual(quiz_summary1.questions_count, 10)
        self.assertEqual(quiz_summary1.participants_count, 25)
        self.assertEqual(quiz_summary1.created_at, "2023-01-15T10:30:00.123456Z")
        self.assertEqual(quiz_summary1.updated_at, "2023-01-16T14:45:00.654321Z")

        quiz_summary2 = result.quizzes[1]
        self.assertEqual(quiz_summary2.id, quiz2.id)
        self.assertEqual(quiz_summary2.title, "Python Advanced")
        self.assertEqual(quiz_summary2.description, "Advanced Python concepts")
        self.assertEqual(quiz_summary2.questions_count, 15)
        self.assertEqual(quiz_summary2.participants_count, 40)
        self.assertEqual(quiz_summary2.created_at, "2023-02-20T08:15:00.987654Z")
        self.assertEqual(quiz_summary2.updated_at, "2023-02-21T16:30:00.456789Z")

        self.quiz_repository_mock.find_by_creator_id.assert_called_once_with(creator_id=self.creator_id)

    def test_handle_success_with_empty_quizzes_list(self):
        self.quiz_repository_mock.find_by_creator_id.return_value = []

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetCreatorQuizzesResponse)
        self.assertEqual(result.creator_id, str(self.creator_id))
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.quizzes), 0)
        self.assertEqual(result.quizzes, [])

        self.quiz_repository_mock.find_by_creator_id.assert_called_once_with(creator_id=self.creator_id)

    def test_handle_success_with_single_quiz(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        quiz.title = "Single Quiz"
        quiz.description = "Only one quiz"
        quiz.total_questions = 5
        quiz.total_participants = 3
        quiz.created_at = datetime(2023, 3, 10, 12, 0, 0, 0)
        quiz.updated_at = datetime(2023, 3, 10, 12, 0, 0, 0)
        quiz.get_formatted_created_at.return_value = "2023-03-10T12:00:00.000000Z"
        quiz.get_formatted_updated_at.return_value = "2023-03-10T12:00:00.000000Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        self.assertEqual(result.total_count, 1)
        self.assertEqual(len(result.quizzes), 1)

        quiz_summary = result.quizzes[0]
        self.assertEqual(quiz_summary.id, quiz.id)
        self.assertEqual(quiz_summary.title, "Single Quiz")
        self.assertEqual(quiz_summary.description, "Only one quiz")
        self.assertEqual(quiz_summary.questions_count, 5)
        self.assertEqual(quiz_summary.participants_count, 3)
        self.assertEqual(quiz_summary.created_at, "2023-03-10T12:00:00.000000Z")
        self.assertEqual(quiz_summary.updated_at, "2023-03-10T12:00:00.000000Z")

    def test_handle_success_with_quiz_no_participants(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
        quiz.title = "New Quiz"
        quiz.description = "Brand new quiz"
        quiz.total_questions = 8
        quiz.total_participants = 0
        quiz.created_at = datetime(2023, 4, 1, 9, 0, 0, 500000)
        quiz.updated_at = datetime(2023, 4, 1, 9, 0, 0, 500000)
        quiz.get_formatted_created_at.return_value = "2023-04-01T09:00:00.500000Z"
        quiz.get_formatted_updated_at.return_value = "2023-04-01T09:00:00.500000Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        quiz_summary = result.quizzes[0]
        self.assertEqual(quiz_summary.participants_count, 0)
        self.assertEqual(quiz_summary.questions_count, 8)

    def test_handle_success_with_quiz_many_questions(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("12312312-3123-1231-2312-312312312312")
        quiz.title = "Comprehensive Quiz"
        quiz.description = "Very detailed quiz"
        quiz.total_questions = 100
        quiz.total_participants = 500
        quiz.created_at = datetime(2023, 5, 15, 14, 30, 0, 750000)
        quiz.updated_at = datetime(2023, 5, 20, 10, 15, 0, 250000)
        quiz.get_formatted_created_at.return_value = "2023-05-15T14:30:00.750000Z"
        quiz.get_formatted_updated_at.return_value = "2023-05-20T10:15:00.250000Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        quiz_summary = result.quizzes[0]
        self.assertEqual(quiz_summary.questions_count, 100)
        self.assertEqual(quiz_summary.participants_count, 500)
        self.assertEqual(quiz_summary.title, "Comprehensive Quiz")

    def test_handle_success_with_different_creator_id(self):
        different_creator_id = UUID("98765432-8765-4321-8765-432187654321")
        different_query = GetCreatorQuizzesQuery(creator_id=str(different_creator_id))

        quiz = Mock(spec=Quiz)
        quiz.id = UUID("abcdefab-cdef-abcd-efab-abcdefabcdef")
        quiz.title = "Different Creator Quiz"
        quiz.description = "Quiz by different creator"
        quiz.total_questions = 12
        quiz.total_participants = 7
        quiz.created_at = datetime(2023, 6, 1, 11, 0, 0, 123000)
        quiz.updated_at = datetime(2023, 6, 1, 11, 0, 0, 123000)
        quiz.get_formatted_created_at.return_value = "2023-06-01T11:00:00.123000Z"
        quiz.get_formatted_updated_at.return_value = "2023-06-01T11:00:00.123000Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(different_query)

        self.assertEqual(result.creator_id, str(different_creator_id))
        self.quiz_repository_mock.find_by_creator_id.assert_called_once_with(creator_id=different_creator_id)

    def test_handle_success_with_long_title_and_description(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("01234567-0123-4567-8901-234567890123")
        quiz.title = "This is a very long quiz title that contains many words and characters to test edge cases"
        quiz.description = "This is an extremely long description that goes on and on with lots of details about the quiz content, objectives, and expectations for participants who will take this comprehensive assessment"
        quiz.total_questions = 20
        quiz.total_participants = 15
        quiz.created_at = datetime(2023, 7, 10, 16, 45, 0, 999999)
        quiz.updated_at = datetime(2023, 7, 15, 8, 30, 0, 111111)
        quiz.get_formatted_created_at.return_value = "2023-07-10T16:45:00.999999Z"
        quiz.get_formatted_updated_at.return_value = "2023-07-15T08:30:00.111111Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        quiz_summary = result.quizzes[0]
        self.assertEqual(
            quiz_summary.title,
            "This is a very long quiz title that contains many words and characters to test edge cases",
        )
        self.assertEqual(
            quiz_summary.description,
            "This is an extremely long description that goes on and on with lots of details about the quiz content, objectives, and expectations for participants who will take this comprehensive assessment",
        )

    def test_handle_success_with_empty_description(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("00000000-0000-0000-0000-000000000001")
        quiz.title = "Quiz with Empty Description"
        quiz.description = ""
        quiz.total_questions = 6
        quiz.total_participants = 2
        quiz.created_at = datetime(2023, 8, 5, 13, 20, 0, 0)
        quiz.updated_at = datetime(2023, 8, 5, 13, 20, 0, 0)
        quiz.get_formatted_created_at.return_value = "2023-08-05T13:20:00.000000Z"
        quiz.get_formatted_updated_at.return_value = "2023-08-05T13:20:00.000000Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        quiz_summary = result.quizzes[0]
        self.assertEqual(quiz_summary.description, "")

    def test_handle_success_datetime_formatting(self):
        quiz = Mock(spec=Quiz)
        quiz.id = UUID("12345678-9012-3456-7890-123456789012")
        quiz.title = "Datetime Test Quiz"
        quiz.description = "Testing datetime formatting"
        quiz.total_questions = 1
        quiz.total_participants = 1
        quiz.created_at = datetime(2023, 12, 31, 23, 59, 59, 999999)
        quiz.updated_at = datetime(2024, 1, 1, 0, 0, 0, 1)
        quiz.get_formatted_created_at.return_value = "2023-12-31T23:59:59.999999Z"
        quiz.get_formatted_updated_at.return_value = "2024-01-01T00:00:00.000001Z"

        self.quiz_repository_mock.find_by_creator_id.return_value = [quiz]

        result = self.handler.handle(self.query)

        quiz_summary = result.quizzes[0]
        self.assertEqual(quiz_summary.created_at, "2023-12-31T23:59:59.999999Z")
        self.assertEqual(quiz_summary.updated_at, "2024-01-01T00:00:00.000001Z")

    def test_handle_success_with_large_number_of_quizzes(self):
        quizzes = []
        for i in range(50):
            quiz = Mock(spec=Quiz)
            quiz.id = UUID(f"12345678-1234-5678-9abc-{i:012d}")
            quiz.title = f"Quiz {i+1}"
            quiz.description = f"Description for quiz {i+1}"
            quiz.total_questions = i + 1
            quiz.total_participants = i * 2
            quiz.created_at = datetime(2023, 1, 1, 0, 0, 0, i * 1000)
            quiz.updated_at = datetime(2023, 1, 1, 0, 0, 0, i * 1000)
            quiz.get_formatted_created_at.return_value = f"2023-01-01T00:00:00.{i*1000:06d}Z"
            quiz.get_formatted_updated_at.return_value = f"2023-01-01T00:00:00.{i*1000:06d}Z"
            quizzes.append(quiz)

        self.quiz_repository_mock.find_by_creator_id.return_value = quizzes

        result = self.handler.handle(self.query)

        self.assertEqual(result.total_count, 50)
        self.assertEqual(len(result.quizzes), 50)

        first_quiz = result.quizzes[0]
        self.assertEqual(first_quiz.title, "Quiz 1")
        self.assertEqual(first_quiz.questions_count, 1)
        self.assertEqual(first_quiz.participants_count, 0)

        last_quiz = result.quizzes[49]
        self.assertEqual(last_quiz.title, "Quiz 50")
        self.assertEqual(last_quiz.questions_count, 50)
        self.assertEqual(last_quiz.participants_count, 98)
