from abc import ABC, abstractmethod

from dto.input import LoginInputDTO
from model import User

token = str


class IAuthService(ABC):
    @abstractmethod
    def login(self, input_dto: LoginInputDTO) -> tuple[User, token]:
        pass
