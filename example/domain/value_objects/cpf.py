class CPF:
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError('CPF must be str')

        if len(value) != 11:
            raise ValueError(f'CPF must be 11 characters long ({len(value)})')

        self.value = value

    def __eq__(self, value):
        return self.value == value

    def __repr__(self):
        return self.value
