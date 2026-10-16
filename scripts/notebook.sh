#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 - "$@" <<'PY'
import json
import pathlib
import sys

if len(sys.argv) < 2:
    sys.exit("Usage: bash scripts/notebook.sh notebooks/<name>.ipynb [arguments]")
root = pathlib.Path.cwd().resolve()
notebook = pathlib.Path(sys.argv[1]).resolve()
if (root / "notebooks") not in notebook.parents or notebook.suffix != ".ipynb":
    sys.exit("Expected a .ipynb inside the repository notebooks directory")
data = json.loads(notebook.read_text())
if data.get("nbformat") != 4:
    sys.exit("Unsupported notebook format")
scope = {"__name__": "__main__", "__file__": str(notebook), "NOTEBOOK_ARGS": sys.argv[2:]}
for index, item in enumerate(data["cells"], 1):
    if item["cell_type"] == "code":
        exec(compile("".join(item["source"]), f"{notebook}:{index}", "exec"), scope)
PY
