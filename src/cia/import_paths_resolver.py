import ast
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional


def resolve_import_paths(import_line: str, base_file: Path, project_root: Path) -> List[Path]:
    """
    Recebe uma linha de importação Python (ex: 'from .. import foo, bar')
    e resolve os caminhos dos módulos importados.

    Args:
        import_line: linha de import (ex: 'from .. import foo, bar')
        base_file: arquivo onde o import está localizado
        project_root: diretório raiz do projeto

    Returns:
        Lista de Paths absolutos para os arquivos importados (se encontrados)
    """
    try:
        node = ast.parse(import_line).body[0]
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            return []
    except Exception:
        return []

    base_module_path = base_file.relative_to(project_root).with_suffix("")  # ex: foo/bar.py
    dotted_path = ".".join(base_module_path.parts)  # ex: foo.bar

    resolved_modules = []

    if isinstance(node, ast.Import):
        # import foo, bar.baz
        for alias in node.names:
            resolved_modules.append(alias.name)

    elif isinstance(node, ast.ImportFrom):
        level = node.level or 0
        from_module = node.module or ""
        for alias in node.names:
            # Pode ser 'from .. import foo' → foo
            mod_name = alias.name
            full_module = _resolve_relative_module(dotted_path, level, from_module, mod_name)
            resolved_modules.append(full_module)

    return list(filter(None, [
        _resolve_module_to_path(mod, project_root)
        for mod in resolved_modules
    ]))


def _resolve_relative_module(current_module: str, level: int, from_module: str, imported_name: str) -> str:
    """Resolve um import relativo com ou sem módulo base"""
    base_parts = current_module.split(".")
    if level > len(base_parts):
        return imported_name  # assume como absoluto se tentar subir demais

    prefix = base_parts[:-level]
    from_parts = from_module.split(".") if from_module else []
    return ".".join(prefix + from_parts + [imported_name])


def _resolve_module_to_path(module_name: str, base_path: Path) -> Optional[Path]:
    """Resolve caminho físico de um módulo Python"""
    sys.path.insert(0, str(base_path))

    try:
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin and spec.origin != "built-in":
            return Path(spec.origin).resolve()
    except ModuleNotFoundError as ex:
        print(f'Could not resolve module "{module_name}" from "{base_path}", considering it as external import')
        return Path(module_name)
    finally:
        sys.path.pop(0)

    return None
