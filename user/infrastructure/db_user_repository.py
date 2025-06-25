from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException
from user.domain.user_repository import UserRepository


class DbUserRepository(UserRepository):

    def find_or_fail_by_id(self, user_id: UUID) -> User:
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist as e:
            raise UserNotFoundException(user_id=user_id) from e

    def find_or_fail_by_email(self, email: str) -> User:
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist as e:
            raise UserNotFoundException(user_email=email) from e
