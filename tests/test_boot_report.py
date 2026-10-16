import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
from support import load
SMOKE = load("scos_smoke", ROOT / "notebooks/smoke.ipynb")

RECORD = {
    "boot_id": "a46bfc7b-5f41-4c06-8e72-1aad2e0caf13",
    "machine_id": "0123456789abcdef0123456789abcdef",
    "eventlog_sha256": "a" * 64,
    "eventlog_bytes": 10009,
    "authorization": "not-evaluated",
}


class BootReportTests(unittest.TestCase):
    def test_dedicated_report_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report"
            path.write_text("SCOS_BOOT_MEASURED " + json.dumps(RECORD) + "\n")
            self.assertEqual(SMOKE.read_boot_report(path), RECORD)

    def test_incomplete_report_is_rejected_until_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report"
            path.write_text('SCOS_BOOT_MEASURED {"machine_id":')
            with self.assertRaises((ValueError, json.JSONDecodeError)):
                SMOKE.read_boot_report(path)

    def test_unverified_attestation_state_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report"
            invalid = {**RECORD, "authorization": "approved"}
            path.write_text("SCOS_BOOT_MEASURED " + json.dumps(invalid) + "\n")
            with self.assertRaises(ValueError):
                SMOKE.read_boot_report(path)

    def test_raw_boot_has_dedicated_virtio_serial_channel(self):
        cmd = SMOKE.qemu_command(
            Path("/tmp/disk.qcow2"), Path("/tmp/code.fd"),
            Path("/tmp/vars.fd"), Path("/tmp/tpm.sock"),
            None, Path("/tmp/boot-report.log"),
        )
        self.assertIn("virtio-serial-pci", cmd)
        self.assertIn("file,id=scos-report,path=/tmp/boot-report.log", cmd)
        self.assertIn(
            "virtserialport,chardev=scos-report,name=org.softcloud.scos.boot", cmd
        )
        installer = SMOKE.qemu_command(
            Path("/tmp/disk.qcow2"), Path("/tmp/code.fd"),
            Path("/tmp/vars.fd"), Path("/tmp/tpm.sock"),
            Path("/tmp/install.iso"),
        )
        self.assertNotIn("virtio-serial-pci", installer)

    def test_interleaved_console_does_not_hide_guest_boot_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            report = directory / "boot-report.log"
            console = directory / "raw-1.log"
            report.write_text("SCOS_BOOT_MEASURED " + json.dumps(RECORD) + "\n")
            qemu = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "-c",
                    (
                        "import sys,time;"
                        "sys.stdout.write('SCOS_BOOT_MEAS[kernel audit]\\nURED {}\\n');"
                        "sys.stdout.flush();time.sleep(15)"
                    ),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            try:
                result = SMOKE.monitor_guest(
                    qemu, console, installing=False, timeout=5, report_path=report
                )
                self.assertEqual(result, RECORD)
            finally:
                SMOKE.stop(qemu)


if __name__ == "__main__":
    unittest.main()
