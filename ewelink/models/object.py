from typing import Any

from pydantic import BaseModel, ConfigDict


class Object(BaseModel):
    model_config = ConfigDict(extra="allow")

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        super().__init__(**(data or {}))
