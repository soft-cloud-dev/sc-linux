"""Load repository tools without installing them or invoking their entrypoints."""

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))


def load(name, path):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
