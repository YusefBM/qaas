import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.infrastructure.views.quizzes_dispatcher_view import QuizzesDispatcherView
from user.domain.user import User


class TestQuizzesDispatcherView(unittest.TestCase):
    def setUp(self):
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_get_view = Mock()
        self.mock_post_view = Mock()
        self.view = QuizzesDispatcherView(get_view=self.mock_get_view, post_view=self.mock_post_view)

    def test_get_delegates_to_get_view(self):
        mock_get_response = Mock()
        mock_get_response.status_code = status.HTTP_200_OK
        mock_get_response.data = {"user_quizzes": [], "total_count": 0}

        self.mock_get_view.get.return_value = mock_get_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_quizzes"], [])
        self.assertEqual(response.data["total_count"], 0)

        self.mock_get_view.get.assert_called_once_with(self.mock_request)

    def test_post_delegates_to_post_view(self):
        mock_post_response = Mock()
        mock_post_response.status_code = status.HTTP_201_CREATED
        mock_post_response.data = {"id": "12345678-1234-5678-9abc-123456789abc"}

        self.mock_post_view.post.return_value = mock_post_response

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], "12345678-1234-5678-9abc-123456789abc")

        self.mock_post_view.post.assert_called_once_with(self.mock_request)
