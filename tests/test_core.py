import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "lib/scos/core.py"


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if MODULE.exists():
            spec = importlib.util.spec_from_file_location("core", MODULE)
            cls.core = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.core)
        else:
            cls.core = None

    def setUp(self):
        self.assertIsNotNone(self.core, "SCOS core implementation is missing")

    def test_explicit_realm_is_preserved(self):
        c = self.core.read_identity(ROOT / "config/identity.json")
        self.assertEqual(c["realm"], "IPA.SOFTCLOUD.DEV")
        self.assertEqual(c["server"], "ipa.softcloud.dev")

    def test_missing_realm_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "identity.json"
            p.write_text('{"server":"ipa.softcloud.dev","domain":"ipa.softcloud.dev"}')
            with self.assertRaises(ValueError):
                self.core.read_identity(p)

    def test_hostname_validation(self):
        self.assertEqual(
            self.core.validate_hostname(
                "node01.ipa.softcloud.dev", "ipa.softcloud.dev"
            ),
            "node01.ipa.softcloud.dev",
        )
        for name in (
            "ipa.softcloud.dev",
            "NODE.ipa.softcloud.dev",
            "-a.ipa.softcloud.dev",
            "x.example.com",
            "x.ipa.softcloud.dev;id",
            "a..ipa.softcloud.dev",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.core.validate_hostname(name, "ipa.softcloud.dev")

    def test_native_password_prompt_not_password_argument(self):
        c = self.core.read_identity(ROOT / "config/identity.json")
        argv = self.core.enrollment_command(
            c, "node01.ipa.softcloud.dev", "/trust/ca.crt"
        )
        self.assertIn("-W", argv)
        self.assertIn("--realm=IPA.SOFTCLOUD.DEV", argv)
        for flag in (
            "--unattended",
            "--permit",
            "--force",
            "--force-join",
            "--ssh-trust-dns",
        ):
            self.assertNotIn(flag, argv)
        self.assertFalse(any(x.startswith("--password") for x in argv))

    def test_payload_hash_and_size_checked(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "payload"
            p.write_bytes(b"scos-image")
            m = self.core.describe_file(p)
            self.core.verify_file(p, m)
            p.write_bytes(b"not-image!")
            with self.assertRaises(ValueError):
                self.core.verify_file(p, m)

    def test_empty_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "empty"
            p.touch()
            with self.assertRaises(ValueError):
                self.core.describe_file(p)

    def test_missing_artifact_rejected(self):
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.core.describe_file(ROOT / "does-not-exist.raw")

    def test_ca_fingerprint_verified_and_private_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            cert = d / "ca.crt"
            key = d / "key.pem"
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
                    str(key),
                    "-out",
                    str(cert),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            digest = self.core.certificate_fingerprint(cert)
            self.assertEqual(len(digest), 64)
            self.core.verify_ca(cert, digest)
            with self.assertRaises(ValueError):
                self.core.verify_ca(cert, "0" * 64)
            with self.assertRaises(ValueError):
                self.core.verify_ca(cert, "")
            cert.write_bytes(cert.read_bytes() + key.read_bytes())
            with self.assertRaises(ValueError):
                self.core.verify_ca(cert, digest)

    def test_leaf_certificate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            cert = d / "leaf.crt"
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
                    "/CN=leaf",
                    "-addext",
                    "basicConstraints=critical,CA:FALSE",
                    "-keyout",
                    str(d / "key"),
                    "-out",
                    str(cert),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self.assertRaises(ValueError):
                self.core.verify_ca(cert, self.core.certificate_fingerprint(cert))

    def test_tree_rejects_keytab_and_ssh_key(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "etc/ssh").mkdir(parents=True)
            self.core.check_tree(root)
            p = root / "etc/krb5.keytab"
            p.write_bytes(b"secret")
            with self.assertRaises(ValueError):
                self.core.check_tree(root)
            p.unlink()
            p = root / "etc/ssh/ssh_host_ed25519_key"
            p.write_bytes(b"secret")
            with self.assertRaises(ValueError):
                self.core.check_tree(root)


if __name__ == "__main__":
    unittest.main()
