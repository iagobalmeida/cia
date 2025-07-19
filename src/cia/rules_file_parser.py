from typing import List

import yaml

from .core import CIARule


def cia_rules_from_file(file_path: str = None) -> List[CIARule]:
    rules = []
    try:
        if file_path == None:
            return rules
        with open(file_path) as rules_file:
            yaml_content = yaml.load(rules_file.buffer, Loader=yaml.FullLoader)
            if isinstance(yaml_content, list):
                return [
                    CIARule(**r) for r in yaml_content
                ]
            return CIARule(**yaml_content)

    except Exception as ex:
        print(f'Failed to load rules: {ex}')
        return rules
