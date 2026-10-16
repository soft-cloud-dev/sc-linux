"""Notebook structure, source/CI boundaries, and local documentation links."""

import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = ("check", "prepare", "make-iso", "artifacts", "footprint", "trust", "seed", "smoke")
GUIDES = ("01-validate", "02-build", "03-inspect", "04-smoke")


class NotebookContractTests(unittest.TestCase):
    def test_host_operations_have_one_notebook_source(self):
        for name in OPERATIONS:
            with self.subTest(name=name):
                self.assertTrue((ROOT / "notebooks" / (name + ".ipynb")).is_file())
                self.assertFalse((ROOT / "scripts" / (name + ".py")).exists())

    def test_all_notebooks_have_parseable_ordered_code_cells(self):
        for name in OPERATIONS + GUIDES:
            with self.subTest(name=name):
                file = ROOT / "notebooks" / (name + ".ipynb")
                document = json.loads(file.read_text())
                self.assertEqual(document["nbformat"], 4)
                self.assertIsInstance(document["cells"], list)
                self.assertGreaterEqual(len(document["cells"]), 3)
                for index, cell in enumerate(document["cells"], 1):
                    self.assertIn(cell["cell_type"], ("code", "markdown"))
                    source = cell["source"]
                    self.assertIsInstance(source, (str, list))
                    if isinstance(source, list):
                        source = "".join(source)
                    if cell["cell_type"] == "code":
                        ast.parse(source, filename=f"{file}:{index}")
                        self.assertIsNone(cell["execution_count"])
                        self.assertEqual(cell["outputs"], [])

    def test_no_old_python_entrypoints_in_build_shell(self):
        for name in ("Makefile", "scripts/build-inside.sh", "scripts/smoke.sh"):
            with self.subTest(file=name):
                source = (ROOT / name).read_text()
                self.assertNotIn("python3 scripts/", source)
                self.assertIn("notebook", source)

    def test_local_markdown_links_exist(self):
        files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
        files.extend((ROOT / "docs").rglob("*.md"))
        files.append(ROOT / "trust/README.md")
        for file in files:
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", file.read_text()):
                address = link.split("#", 1)[0].split("?", 1)[0]
                if not address or "://" in address or address.startswith(("mailto:", "/")):
                    continue
                with self.subTest(file=str(file.relative_to(ROOT)), link=link):
                    self.assertTrue((file.parent / address).exists(), f"Broken local link: {link}")


if __name__ == "__main__":
    unittest.main()
