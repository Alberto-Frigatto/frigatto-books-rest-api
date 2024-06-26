from abc import ABC, abstractmethod

from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from model import User

file_path = str
mimetype = str


class IUserController(ABC):
    @abstractmethod
    def create_user(self, input_dto: CreateUserInputDTO) -> User:
        pass

    @abstractmethod
    def get_current_user(self) -> User:
        pass

    @abstractmethod
    def get_user_photo(self, filename: str) -> tuple[file_path, mimetype]:
        pass

    @abstractmethod
    def update_user(self, input_dto: UpdateUserInputDTO) -> User:
        pass
