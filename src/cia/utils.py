import re
from enum import StrEnum
from pathlib import Path


class bcolors(StrEnum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


RESULTS_ICONS = {
    True: f'{bcolors.OKGREEN}✔{bcolors.ENDC}',
    False: f'{bcolors.FAIL}✖{bcolors.ENDC}'
}

RESULT_COLORS = {
    True: None,
    False: f'{bcolors.UNDERLINE}{bcolors.FAIL}'
}


def path_to_name(path: Path) -> str:
    if path.parts[-1] == '__init__.py':
        return f'{path.parts[-2]}'
    else:
        return f'{path.parts[-1]}'
