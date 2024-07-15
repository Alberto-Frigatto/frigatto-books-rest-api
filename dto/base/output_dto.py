from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict

from model.base import Model


class OutputDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def dump(cls, model: Model) -> dict[str, Any]:
        dto = cls(**model.__dict__)
        serialization = dto.model_dump()

        return serialization

    @classmethod
    def dump_many(cls, models: Sequence[Model]) -> list[dict[str, Any]]:
        serialization = [cls.dump(model) for model in models]

        return serialization
