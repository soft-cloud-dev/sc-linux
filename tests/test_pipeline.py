import pathlib
import unittest
from support import load

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_smoke_requires_real_inputs(self):
        module = load("smoke", ROOT / "notebooks/smoke.ipynb")
        self.assertIsNotNone(module, "Boot smoke harness is missing")
        with self.assertRaises(ValueError):
            module.require_inputs(ROOT / "tests/does-not-exist")

    def test_smoke_parses_only_evidence_marker(self):
        module = load("smoke2", ROOT / "notebooks/smoke.ipynb")
        self.assertIsNotNone(module, "Boot evidence parser is missing")
        record = module.parse_measurement(
            'noise\nSCOS_BOOT_MEASURED {"machine_id":"abc", "authorization":"not-evaluated"}\n'
        )
        self.assertEqual(record["machine_id"], "abc")
        with self.assertRaises(ValueError):
            module.parse_measurement("firmware started")

    def test_image_workflow_is_manual_and_read_only(self):
        p = ROOT / ".github/workflows/build.yml"
        self.assertTrue(p.is_file(), "Build workflow missing")
        text = p.read_text()
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("id-token: write", text)
        self.assertIn("make smoke", text)
        self.assertIn("if-no-files-found: error", text)


if __name__ == "__main__":
    unittest.main()
