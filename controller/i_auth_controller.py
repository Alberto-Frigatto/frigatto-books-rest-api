from abc import ABC, abstractmethod

from dto.input import LoginInputDTO
from model import User

token = str


class IAuthController(ABC):
    @abstractmethod
    def login(self, input_dto: LoginInputDTO) -> tuple[User, token]:
        pass
