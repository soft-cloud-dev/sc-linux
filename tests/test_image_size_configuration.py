"""Prevent unintended regressions of mkosi footprint configuration."""

import configparser
import unittest

from support import ROOT


class ImageSizeConfigurationTests(unittest.TestCase):
    def config(self, image):
        config = configparser.ConfigParser(interpolation=None)
        config.read(ROOT / "images" / image / "mkosi.conf")
        return config

    def test_recommends_and_docs_disabled(self):
        for image in ("server", "installer"):
            with self.subTest(image=image):
                config = self.config(image)["Content"]
                self.assertEqual(config["WithRecommends"], "no")
                self.assertEqual(config["WithDocs"], "no")

    def test_dynamic_root_partition(self):
        root = (ROOT / "images/server/mkosi.repart/10-root.conf").read_text()
        esp = (ROOT / "images/server/mkosi.repart/00-esp.conf").read_text()
        self.assertIn("SizeMinBytes=2G", root)
        self.assertIn("Minimize=guess", root)
        self.assertIn("GrowFileSystem=yes", root)
        self.assertNotIn("SizeMaxBytes=", root)
        self.assertIn("SizeMinBytes=384M", esp)
        self.assertIn("SizeMaxBytes=384M", esp)
        self.assertIn("systemd-repart", self.config("server")["Content"]["Packages"])
        self.assertTrue(
            (ROOT / "images/server/overlay/usr/lib/repart.d/50-root.conf").is_file()
        )

    def test_compression_and_report_generation(self):
        build = (ROOT / "scripts/build-inside.sh").read_text()
        self.assertIn("zstd -T1 -19 --no-progress", build)
        self.assertIn("python3 scripts/footprint.py /out", build)
        self.assertTrue(
            (ROOT / "images/installer/mkosi.finalize.chroot").is_file()
        )


if __name__ == "__main__":
    unittest.main()
