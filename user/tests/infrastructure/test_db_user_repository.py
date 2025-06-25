import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException
from user.infrastructure.db_user_repository import DbUserRepository


class TestDbUserRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbUserRepository()
        self.user_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_email = "test@example.com"

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_id_success(self, mock_objects):
        expected_user = Mock(spec=User)
        expected_user.id = self.user_id
        expected_user.email = self.user_email
        expected_user.username = "testuser"

        mock_objects.get.return_value = expected_user

        result = self.repository.find_or_fail_by_id(self.user_id)

        self.assertEqual(result, expected_user)
        mock_objects.get.assert_called_once_with(id=self.user_id)

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_id_raises_user_not_found_exception(self, mock_objects):
        mock_objects.get.side_effect = ObjectDoesNotExist

        with self.assertRaises(UserNotFoundException) as context:
            self.repository.find_or_fail_by_id(self.user_id)

        self.assertEqual(context.exception.user_id, self.user_id)
        mock_objects.get.assert_called_once_with(id=self.user_id)

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_email_success(self, mock_objects):
        expected_user = Mock(spec=User)
        expected_user.id = self.user_id
        expected_user.email = self.user_email
        expected_user.username = "testuser"

        mock_objects.get.return_value = expected_user

        result = self.repository.find_or_fail_by_email(self.user_email)

        self.assertEqual(result, expected_user)
        mock_objects.get.assert_called_once_with(email=self.user_email)

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_email_raises_user_not_found_exception(self, mock_objects):
        mock_objects.get.side_effect = ObjectDoesNotExist

        with self.assertRaises(UserNotFoundException) as context:
            self.repository.find_or_fail_by_email(self.user_email)

        self.assertEqual(context.exception.user_email, self.user_email)
        mock_objects.get.assert_called_once_with(email=self.user_email)

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_email_with_different_email_address(self, mock_objects):
        different_email = "different@example.com"
        expected_user = Mock(spec=User)
        expected_user.email = different_email

        mock_objects.get.return_value = expected_user

        result = self.repository.find_or_fail_by_email(different_email)

        self.assertEqual(result, expected_user)
        mock_objects.get.assert_called_once_with(email=different_email)

    @patch("user.domain.user.User.objects")
    def test_find_or_fail_by_id_with_different_user_id(self, mock_objects):
        different_user_id = UUID("87654321-4321-8765-cba9-987654321098")
        expected_user = Mock(spec=User)
        expected_user.id = different_user_id

        mock_objects.get.return_value = expected_user

        result = self.repository.find_or_fail_by_id(different_user_id)

        self.assertEqual(result, expected_user)
        mock_objects.get.assert_called_once_with(id=different_user_id)
