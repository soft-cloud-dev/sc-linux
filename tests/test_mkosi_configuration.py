from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
from support import load
CHECK = load("scos_check", ROOT / "notebooks/check.ipynb")


class MkosiPackagesTests(unittest.TestCase):
    def test_repository_image_package_lists(self):
        CHECK.check_mkosi_packages()

    def test_multiline_package_specifications(self):
        self.assertEqual(
            CHECK.parse_mkosi_packages("linux-image-amd64\n    systemd-sysv\n    udev"),
            ["linux-image-amd64", "systemd-sysv", "udev"],
        )

    def test_comma_separated_package_specifications(self):
        self.assertEqual(
            CHECK.parse_mkosi_packages("linux-image-amd64, systemd-sysv, udev"),
            ["linux-image-amd64", "systemd-sysv", "udev"],
        )

    def test_space_separated_group_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "one package per line"):
            CHECK.parse_mkosi_packages("linux-image-amd64 systemd-sysv\n udev")

    def test_empty_package_list_is_rejected(self):
        with self.assertRaises(ValueError):
            CHECK.parse_mkosi_packages(" \n ")


if __name__ == "__main__":
    unittest.main()
