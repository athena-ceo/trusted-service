from abc import ABC

from pydantic import BaseModel


class Localization(BaseModel, ABC):
    pass
