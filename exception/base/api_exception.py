from datetime import datetime, timezone
from typing import Any


class ApiException(Exception):
    def __init__(self, *, message: str, status: int, detail: Any | None = None) -> None:
        self._name = self.__class__.__name__
        self._message = message
        self._status = status
        self._scope = self.__class__.__qualname__.split('.')[0]
        self._detail = detail
        self._timestamp = datetime.now(timezone.utc).isoformat()

        super().__init__()

    def searialize(self) -> dict[str, Any]:
        serialization = {
            'code': self._name,
            'scope': self._scope,
            'message': self._message,
            'status': self._status,
            'timestamp': self._timestamp,
        }

        if self._detail is not None:
            serialization['detail'] = self._detail

        return serialization

    @property
    def status(self) -> int:
        return self._status
