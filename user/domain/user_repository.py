from abc import ABC, abstractmethod
from uuid import UUID

from user.domain.user import User


class UserRepository(ABC):
    @abstractmethod
    def find_or_fail_by_id(self, user_id: UUID) -> User:
        pass

    @abstractmethod
    def find_or_fail_by_email(self, email: str) -> User:
        pass
