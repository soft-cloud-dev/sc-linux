"""Load notebooks or guest commands as modules without running their entrypoints."""
import importlib.util
import json
import sys
import types
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))


def load(name, path):
    if path.suffix == ".ipynb":
        module = types.ModuleType(name)
        module.__file__ = str(path)
        for index, cell in enumerate(json.loads(path.read_text())["cells"], 1):
            if cell["cell_type"] == "code":
                source = cell["source"]
                if isinstance(source, list):
                    source = "".join(source)
                exec(compile(source, f"{path}:{index}", "exec"), module.__dict__)
        return module
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
