from dto.base import OutputDTO


class UserOutputDTO(OutputDTO):
    id: int
    username: str
    img_url: str
