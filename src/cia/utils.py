from pathlib import Path


def print_table(headers, rows):
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]

    def format_row(row):
        return " | ".join(str(val).ljust(width) for val, width in zip(row, col_widths))

    print(format_row(headers))
    print(" + ".join(' ' * w for w in col_widths))
    for row in rows:
        print(format_row(row))


RESULTS_ICONS = {
    True: '✔',
    False: '✖'
}


def path_to_name(path: Path) -> str:
    if path.parts[-1] == '__init__.py':
        return f'{path.parts[-2]}'
    else:
        return f'{path.parts[-1]}'
