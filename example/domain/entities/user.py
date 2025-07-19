from dataclasses import dataclass

from .. import value_objects


@dataclass
class User:
    name: str
    document: value_objects.cpf.CPF
