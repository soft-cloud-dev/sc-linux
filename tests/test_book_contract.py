"""Structural and safety checks for the Jupyter Book laboratory."""

import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CHAPTERS = (
    "01-environment", "02-configuration", "03-trust",
    "04-builder", "05-image", "06-artifacts",
    "07-boot", "08-provision", "09-reproducibility",
)


class BookContractTests(unittest.TestCase):
    def test_project_toc_lists_every_chapter_in_order(self):
        toc = (ROOT / "myst.yml").read_text()
        files = re.findall(r"^\s+- file: ([^\s#]+)", toc, flags=re.MULTILINE)
        expected = ["book/index.md", *[f"book/{n}.ipynb" for n in CHAPTERS], "book/appendix.md"]
        self.assertEqual(files, expected)
        for relative in files:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_chapters_are_actionable_and_not_executed_by_site(self):
        for name in CHAPTERS:
            with self.subTest(chapter=name):
                path = BOOK / f"{name}.ipynb"
                doc = json.loads(path.read_text())
                self.assertEqual(doc["nbformat"], 4)
                self.assertIn("skip-execution", doc.get("metadata", {}).get("tags", []))
                markdown = "\n".join(
                    c["source"] if isinstance(c["source"], str) else "".join(c["source"])
                    for c in doc["cells"] if c["cell_type"] == "markdown"
                )
                for marker in ("## Goal", "## Prerequisites", "## Action", "## Check", "## Next"):
                    self.assertIn(marker, markdown)
                code = [c for c in doc["cells"] if c["cell_type"] == "code"]
                self.assertGreaterEqual(len(code), 2)
                for index, cell in enumerate(code, 1):
                    source = cell["source"]
                    if isinstance(source, list):
                        source = "".join(source)
                    ast.parse(source, filename=f"{path}:{index}")
                    self.assertIsNone(cell["execution_count"])
                    self.assertEqual(cell["outputs"], [])

    def test_internal_links_resolve(self):
        files = [BOOK / "index.md", BOOK / "appendix.md"]
        files.extend(BOOK.glob("*.ipynb"))
        for path in files:
            if path.suffix == ".ipynb":
                doc = json.loads(path.read_text())
                sources = [
                    c["source"] if isinstance(c["source"], str) else "".join(c["source"])
                    for c in doc["cells"] if c["cell_type"] == "markdown"
                ]
            else:
                sources = [path.read_text()]
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", "\n".join(sources)):
                relative = link.split("#", 1)[0].split("?", 1)[0]
                if not relative or "://" in relative or relative.startswith(("/", "mailto:")):
                    continue
                with self.subTest(page=path.name, link=link):
                    self.assertTrue((path.parent / relative).exists(), f"Missing link: {link}")

    def test_book_lab_does_not_write_to_source(self):
        script = (ROOT / "scripts/book-lab.sh").read_text()
        self.assertIn("build/book-notebooks", script)
        self.assertIn('for source in book/*.ipynb', script)
        self.assertIn("ServerApp.root_dir", script)
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn("book-lab:", makefile)
        self.assertIn("jupyter book build --html", makefile)
        self.assertNotIn("jupyter book build --execute", makefile)


if __name__ == "__main__":
    unittest.main()
