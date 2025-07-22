import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import List

from .import_paths_resolver import resolve_import_paths
from .utils import RESULTS_ICONS, path_to_name, print_table


class CIAModule:
    class Import:
        def __init__(self, import_line: str, file_path: str, valid: bool = True, invalid_rules_name: List[str] = None):
            self.import_line = import_line
            self.file_path = file_path
            self.name = path_to_name(file_path)
            self.valid = valid
            self.invalid_rules_name = invalid_rules_name if invalid_rules_name else []

    imports: List[Import]

    def __init__(self, root_path: Path, file_path: Path):
        self.name = path_to_name(file_path)
        self.root_path = root_path
        self.file_path = file_path
        self.folder_depth = len(str(file_path).split('/'))
        self.content = None
        self.imports = []

    @property
    def valid(self):
        return all([
            i.valid for i in self.imports
        ])

    @property
    def mermaid_node_name(self) -> str:
        return self.name.replace('.py', '')

    @property
    def mermaid_node_prefix(self) -> str:
        if self.name.endswith('.py'):
            return '['
        return '[['

    @property
    def mermaid_node_sufix(self) -> str:
        if self.name.endswith('.py'):
            return ']'
        return ']]'

    @property
    def mermaid_node_line(self) -> str:
        return ''.join([
            '\t',
            self.mermaid_node_name,
            self.mermaid_node_prefix,
            self.name,
            self.mermaid_node_sufix
        ])

    def resolve_imports(self) -> List[Exception]:
        if not self.content:
            self.load_content()

        excs = []
        for line in self.content.splitlines():
            if not line.startswith('from'):
                continue

            try:
                paths = resolve_import_paths(
                    import_line=line,
                    base_file=self.file_path,
                    project_root=self.root_path
                )

                for path in paths:
                    self.imports.append(
                        CIAModule.Import(import_line=line, file_path=path)
                    )
            except Exception as exc:
                excs.append(exc)

        return excs

    # TODO: Use `ast` to parse imports
    def load_content(self):
        content = self.file_path.read_text(encoding='utf-8')

        def replacer(match):
            from_part = match.group("from_part")
            imports_raw = match.group("imports")
            # Remove quebras de linha, comentários e espaços extras
            imports = re.sub(r"#.*", "", imports_raw)  # remove comentários
            imports = re.sub(r"\s+", " ", imports)     # substitui espaços múltiplos por um único espaço
            imports = imports.strip().strip(",")       # remove vírgulas e espaços extras das pontas
            return f"{from_part} import {imports}"

        # Regex que pega from ... import ( multiline ... )
        pattern = re.compile(
            r"(?P<from_part>from\s+[^\n]+?)\s+import\s*\(\s*(?P<imports>.*?)\s*\)",
            re.DOTALL
        )

        self.content = pattern.sub(replacer, content)


class CIARule:
    class Modality(StrEnum):
        ALLOWED = 'allowed'
        NOT_ALLOWED = "not_allowed"

    name: str
    modality: Modality
    source: str
    target: str

    def __init__(self, name: str, modality: Modality, source: str, target: str):
        self.name = name
        self.modality = modality
        self.source = source
        self.target = target

    def validate_module(self, cia_module: CIAModule):
        if self.modality == CIARule.Modality.ALLOWED:
            for i in cia_module.imports:
                i.valid = True
            return

        for cia_import in cia_module.imports:
            try:
                if re.match(self.source, str(cia_import.file_path)) and re.match(self.target, str(cia_module.file_path)):
                    cia_import.valid = False
                    cia_import.invalid_rules_name.append(self.name)
            except Exception as ex:
                print(f'Failed to apply rule "{self.name}" on "{cia_module.name}": {ex}')


@dataclass
class CIAConfig:
    table: bool = True
    table_valid: bool = True
    mermaid: bool = True
    mermaid_output: str = None
    debug: bool = False


class CIA:

    base_path: Path
    modules: List[CIAModule] = []
    rules: List[CIARule] = []

    def __init__(self, base_dir: str, config: CIAConfig = CIAConfig(), rules: List[CIARule] = [], load: bool = True):
        self.base_path = Path(base_dir).resolve()
        self.config = config
        self.rules = rules
        self.total_modules = 0
        if load:
            self.load_modules()

    @property
    def total_invalid_modules(self) -> int:
        return len([m for m in self.modules if not m.valid])

    @property
    def total_invalid_imports(self) -> int:
        return sum([len([i for i in m.imports if not i.valid]) for m in self.modules])

    def load_modules(self):
        all_paths = self.base_path.rglob('*')
        for path in all_paths:
            if not path.is_file() or not path.suffix == '.py':
                continue

            cia_module = CIAModule(
                root_path=self.base_path,
                file_path=path
            )
            excs = cia_module.resolve_imports()

            if excs and self.config.debug:
                for exc in excs:
                    print(exc)

            self.total_modules += 1
            self.modules.append(cia_module)

    def apply_rules(self):
        for rule in self.rules:
            for module in self.modules:
                rule.validate_module(module)

    def mermaid(self):
        lines = ['graph TB']
        styleLines = ['\tclassDef invalidNode stroke:#f00,stroke-width:4px;']
        invalid_nodes = []

        curr = 0
        for module in self.modules:
            lines.append(module.mermaid_node_line)
            if not module.valid:
                invalid_nodes.append(module.mermaid_node_name)

            for index, i in enumerate(module.imports):
                actual_index = curr + index
                node_target = i.name.replace('.py', '')
                lines.append(f'\t{node_target} -- "{i.import_line}" --> {module.mermaid_node_name}')
                if not i.valid:
                    styleLines.append(f'\tlinkStyle {actual_index} stroke:#f00')
            curr += len(module.imports)

        output_file = self.config.mermaid_output
        if not output_file:
            output_file = f'./{self.base_path.parts[-1]}.mmd'

        with open(output_file, 'w') as file:
            file.write(f'\n'.join(lines))
            file.write(f'\n')
            file.write(f'\n'.join(styleLines))
            file.write(f'\n class {",".join(invalid_nodes)} invalidNode;')

    def table(self):
        print(f'\nCIA! Open the door!')
        print(f'{self.total_modules} modules analised')
        print(f'{self.total_invalid_modules} invalid modules')
        print(f'{self.total_invalid_imports} invalid imports\n')
        cols = ['Module Name', 'Module Path', 'Import Name', 'Import Path', 'Valid', 'Invalid Rules']
        rows = []
        for module in self.modules:
            if module.valid and not self.config.table_valid:
                continue

            rows.append([
                module.name,
                module.file_path,
                '',
                '',
                RESULTS_ICONS[module.valid],
                ''
            ])
            for i in module.imports:
                rows.append([
                    '',
                    '',
                    i.name,
                    i.file_path,
                    RESULTS_ICONS[i.valid],
                    i.invalid_rules_name
                ])
        print_table(cols, rows)
