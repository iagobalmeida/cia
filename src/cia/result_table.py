import re
from typing import Any, List

from .utils import bcolors

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def visible_len(text):
    return len(ANSI_ESCAPE.sub('', str(text)))


class ResultRow:
    color: bcolors = None
    values: List[Any]

    def __init__(self, values: List[Any], color: bcolors = None):
        self.values = values
        self.color = color

        if self.color:
            self.values = [
                f'{self.color}{v}{bcolors.ENDC}' for v in self.values
            ]


class ResultTable:
    def __init__(self, headers: List[str], rows: List[ResultRow], header_color: bcolors = bcolors.HEADER):
        self.rows = rows
        self.header_color = header_color
        self.headers = headers

    def print(self):
        print('\n')
        self.headers = [
            f'{self.header_color}{h}{bcolors.ENDC}' for h in self.headers
        ]
        col_widths = [
            max(visible_len(item) for item in col)
            for col in zip(self.headers, *[r.values for r in self.rows])
        ]

        def format_row(row):
            padded = []
            for val, width in zip(row, col_widths):
                val_str = str(val)
                pad_len = width - visible_len(val_str)
                padded.append(val_str + ' ' * pad_len)
            return " | ".join(padded)

        print(format_row(self.headers))
        print("-+-".join('-' * w for w in col_widths))
        for row in self.rows:
            print(format_row(row.values))
