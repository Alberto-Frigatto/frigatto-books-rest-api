from injector import inject

from dto.input import CreateUserInputDTO, UpdateUserInputDTO
from model import User
from service import IUserService

from .. import IUserController

file_path = str
mimetype = str


@inject
class UserController(IUserController):
    def __init__(self, service: IUserService) -> None:
        self.service = service

    def create_user(self, input_dto: CreateUserInputDTO) -> User:
        return self.service.create_user(input_dto)

    def get_current_user(self) -> User:
        return self.service.get_current_user()

    def get_user_photo(self, filename: str) -> tuple[file_path, mimetype]:
        return self.service.get_user_photo(filename)

    def update_user(self, input_dto: UpdateUserInputDTO) -> User:
        return self.service.update_user(input_dto)

    def delete_user(self) -> None:
        self.service.delete_user()
