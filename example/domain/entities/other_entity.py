from dataclasses import dataclass

from example.application import (
    other_service
)


@dataclass
class OtherEntity:
    name: str

    def foo():
        other_service.dont_import_me()
