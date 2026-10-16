"""Regression tests for importable commands and extracted disk-readback checks."""

import hashlib
import io
import pathlib
import subprocess
import sys
import unittest

from support import ROOT, load


class CommandTests(unittest.TestCase):
    def test_host_tools_can_be_imported_without_running_cli(self):
        for script in (
            "check.ipynb",
            "artifacts.ipynb",
            "prepare.ipynb",
            "seed.ipynb",
            "trust.ipynb",
            "make-iso.ipynb",
            "smoke.ipynb",
        ):
            with self.subTest(script=script):
                module = load(script.replace(".", "_"), ROOT / "notebooks" / script)
                self.assertTrue(callable(module.main))

    def test_public_cli_help_does_not_require_build_inputs(self):
        for script in (
            "check.ipynb",
            "artifacts.ipynb",
            "seed.ipynb",
            "trust.ipynb",
            "make-iso.ipynb",
            "smoke.ipynb",
        ):
            with self.subTest(script=script):
                result = subprocess.run(
                    ["bash", "scripts/notebook.sh", str(ROOT / "notebooks" / script), "--help"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_disk_readback_checks_exact_payload_size_and_hash(self):
        installer = load(
            "installer_readback",
            ROOT / "images/installer/overlay/usr/local/sbin/scos-install",
        )
        self.assertTrue(callable(getattr(installer, "verify_readback", None)))
        data = b"server-image"
        expected = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        installer.verify_readback(io.BytesIO(data + b"unused-disk-space"), expected)
        for actual in (b"too-short", b"corrupt-data"):
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                installer.verify_readback(io.BytesIO(actual), expected)

    def test_boot_record_requires_unique_id_format_and_no_attestation_claim(self):
        smoke = load("smoke_validation", ROOT / "notebooks/smoke.ipynb")
        self.assertTrue(callable(getattr(smoke, "validate_measurement", None)))
        valid = {"machine_id": "a" * 32, "authorization": "not-evaluated"}
        self.assertEqual(smoke.validate_measurement(valid), valid)
        for changes in (
            {"machine_id": ""},
            {"machine_id": "not-a-machine-id"},
            {"authorization": "approved"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                smoke.validate_measurement(valid | changes)


if __name__ == "__main__":
    unittest.main()
