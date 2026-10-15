"""Check that the relocated inputs produce complete server and installer trees."""

import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from support import ROOT, load


class StagingTests(unittest.TestCase):
    def test_preparation_copies_both_overlays_and_shared_package(self):
        prepare = load("prepare", ROOT / "scripts/prepare.py")
        self.assertTrue(callable(getattr(prepare, "prepare", None)))
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for directory in ("config", "images", "lib"):
                shutil.copytree(ROOT / directory, root / directory)
            trust = root / "trust"
            trust.mkdir()
            certificate = trust / "ipa-ca.crt"
            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-new",
                    "-x509",
                    "-newkey",
                    "rsa:2048",
                    "-nodes",
                    "-days",
                    "2",
                    "-subj",
                    "/CN=SCOS TEST ONLY",
                    "-addext",
                    "basicConstraints=critical,CA:TRUE",
                    "-keyout",
                    str(root / "temporary.key"),
                    "-out",
                    str(certificate),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            from scos.core import certificate_fingerprint

            (trust / "ipa-ca.sha256").write_text(certificate_fingerprint(certificate))
            prepare.prepare(root, source_commit="a" * 40, source_date_epoch=1700000000)
            for image, command in (
                ("server", "scos-enroll"),
                ("installer", "scos-install"),
            ):
                overlay = root / "build" / f"{image}-overlay"
                self.assertTrue((overlay / "usr/local/lib/scos/core.py").is_file())
                self.assertTrue((overlay / "usr/local/lib/scos/__init__.py").is_file())
                self.assertEqual(
                    (overlay / f"usr/local/sbin/{command}").stat().st_mode & 0o777,
                    0o755,
                )
                metadata = json.loads(
                    (overlay / "usr/local/share/scos/build.json").read_text()
                )
                self.assertEqual(metadata["source_commit"], "a" * 40)
                self.assertEqual(metadata["source_date_epoch"], 1700000000)
                self.assertEqual(list(overlay.rglob("*.pyc")), [])
            server = root / "build/server-overlay"
            self.assertEqual(
                (server / "usr/local/share/ca-certificates/scos-ipa.crt").read_bytes(),
                certificate.read_bytes(),
            )
            self.assertEqual(
                (server / "usr/local/share/scos/identity.json").read_bytes(),
                (root / "config/identity.json").read_bytes(),
            )
            apt = server / "etc/apt/sources.list.d/trixie.sources"
            self.assertIn("Check-Valid-Until: no", apt.read_text())
            self.assertIn("Signed-By:", apt.read_text())
            # Re-running preparation replaces stale output instead of merging it.
            stale = server / "stale-file"
            stale.touch()
            prepare.prepare(root, source_commit="b" * 40, source_date_epoch=1700000001)
            self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
