from example import domain


def create_user(name: str, document: str) -> domain.entities.user.User:
    return domain.entities.user.User(
        name=name,
        document=domain.value_objects.CPF(document)
    )
