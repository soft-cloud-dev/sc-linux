import pathlib
import tempfile
import unittest

from support import ROOT, load


class ProvisioningTests(unittest.TestCase):
    def test_seed_contains_no_password_or_otp(self):
        module = load("seed", ROOT / "notebooks/seed.ipynb")
        self.assertIsNotNone(module, "Seed utility is missing")
        data = module.user_data(
            "node01.ipa.softcloud.dev", "ssh-ed25519 AAAATEST public-only"
        )
        self.assertTrue(data["disable_root"])
        self.assertFalse(data["ssh_pwauth"])
        self.assertNotIn("password", str(data))
        self.assertNotIn("otp", str(data))
        self.assertEqual(data["fqdn"], "node01.ipa.softcloud.dev")

    def test_installer_refuses_mounted_or_wrong_type_disk(self):
        module = load(
            "installer", ROOT / "images/installer/overlay/usr/local/sbin/scos-install"
        )
        self.assertIsNotNone(module, "Installer utility is missing")
        good = {
            "path": "/dev/vda",
            "type": "disk",
            "size": 8000,
            "ro": False,
            "mountpoints": [None],
        }
        self.assertEqual(module.validate_disk(good, "/dev/vda", 4000), "/dev/vda")
        for change in (
            {"type": "part"},
            {"size": 1000},
            {"ro": True},
            {"mountpoints": ["/"]},
            {"children": [{"mountpoints": ["/boot"]}]},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                module.validate_disk(good | change, "/dev/vda", 4000)

    def test_installer_refuses_wrong_device(self):
        module = load(
            "installer", ROOT / "images/installer/overlay/usr/local/sbin/scos-install"
        )
        self.assertIsNotNone(module, "Installer utility is missing")
        with self.assertRaises(ValueError):
            module.validate_disk(
                {"path": "/dev/sda", "type": "disk", "size": 9000, "ro": False},
                "/dev/vda",
                4000,
            )

    def test_both_recipes_are_present(self):
        for path in (
            "images/server/mkosi.conf",
            "images/installer/mkosi.conf",
            "scripts/build-inside.sh",
            "notebooks/make-iso.ipynb",
        ):
            self.assertTrue((ROOT / path).is_file(), path + " is missing")


class EnrollmentConfigurationTests(unittest.TestCase):
    def test_ipa_global_section_is_required(self):
        import tempfile

        module = load(
            "enrollment", ROOT / "images/server/overlay/usr/local/sbin/scos-enroll"
        )
        self.assertTrue(
            hasattr(module, "verify_configuration"),
            "IPA global section validator is missing",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "default.conf"
            path.write_text(
                "[global]\nrealm = IPA.SOFTCLOUD.DEV\ndomain = ipa.softcloud.dev\n"
            )
            module.verify_configuration(
                path, {"realm": "IPA.SOFTCLOUD.DEV", "domain": "ipa.softcloud.dev"}
            )
            path.write_text(
                "[global]\nrealm = WRONG.REALM\ndomain = ipa.softcloud.dev\n"
            )
            with self.assertRaises(ValueError):
                module.verify_configuration(
                    path, {"realm": "IPA.SOFTCLOUD.DEV", "domain": "ipa.softcloud.dev"}
                )


if __name__ == "__main__":
    unittest.main()
