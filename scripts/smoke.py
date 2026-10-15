#!/usr/bin/env python3
"""Boot two RAW clones; install the ISO to a blank virtual disk and boot it."""

import argparse
import json
import os
import pathlib
import re
import selectors
import shutil
import subprocess
import tempfile
import time
import uuid


def require_inputs(output):
    for relative in ("raw/sc-linux.raw", "sc-linux.iso"):
        p = pathlib.Path(output) / relative
        if not p.is_file() or p.stat().st_size < 1024 * 1024:
            raise ValueError("Missing or invalid boot artifact: " + str(p))


def parse_measurement(text):
    for line in text.splitlines():
        if "SCOS_BOOT_MEASURED " in line:
            return json.loads(line.split("SCOS_BOOT_MEASURED ", 1)[1].strip())
    raise ValueError("Guest did not produce boot evidence")


def validate_measurement(record):
    """Require initialized identity without inventing an authorization verdict."""
    if not re.fullmatch("[0-9a-f]{32}", record.get("machine_id", "")):
        raise ValueError("Guest machine ID was not initialized")
    if record.get("authorization") != "not-evaluated":
        raise ValueError("Smoke test must not claim attestation authorization")
    return record


def wait_path(path, proc, seconds=10):
    deadline = time.monotonic() + seconds
    while not path.exists():
        if proc.poll() is not None:
            raise RuntimeError("swtpm exited before its socket became available")
        if time.monotonic() > deadline:
            raise TimeoutError("swtpm socket timeout")
        time.sleep(0.1)


def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)


def monitor_guest(qemu, log_path, *, installing, timeout):
    """Persist console output and wait for the expected boot or install marker."""
    with selectors.DefaultSelector() as selector:
        selector.register(qemu.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        text = ""
        invoked = False
        confirmed = False
        with log_path.open("wb") as logfile:
            while time.monotonic() < deadline:
                for key, _ in selector.select(timeout=1):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        continue
                    logfile.write(data)
                    logfile.flush()
                    text += data.decode(errors="replace")
                    if installing and not invoked and "SCOS_INSTALLER_READY" in text:
                        qemu.stdin.write(b"scos-install /dev/vda\n")
                        qemu.stdin.flush()
                        invoked = True
                    if (
                        installing
                        and not confirmed
                        and "Type ERASE /dev/vda to continue:" in text
                    ):
                        qemu.stdin.write(b"ERASE /dev/vda\n")
                        qemu.stdin.flush()
                        confirmed = True
                    if installing and "SCOS_INSTALL_COMPLETE" in text:
                        return None
                    if not installing and "SCOS_BOOT_MEASURED " in text:
                        try:
                            record = parse_measurement(text)
                        except (ValueError, json.JSONDecodeError):
                            continue
                        return validate_measurement(record)
                if qemu.poll() is not None:
                    raise RuntimeError(
                        "Guest exited without reaching its acceptance marker"
                    )
        raise TimeoutError("Guest did not finish; inspect " + str(log_path))


def qemu_command(disk, code, variables, control, iso):
    """Use isolated firmware variables, a software TPM, and no network interface."""
    accel = "kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "tcg"
    command = [
        "qemu-system-x86_64",
        "-machine",
        "q35,accel=" + accel,
        "-m",
        "4096",
        "-smp",
        "2",
        "-uuid",
        str(uuid.uuid4()),
        "-display",
        "none",
        "-serial",
        "stdio",
        "-monitor",
        "none",
        "-no-reboot",
        "-nic",
        "none",
        "-drive",
        "if=pflash,unit=0,format=raw,readonly=on,file=" + str(code),
        "-drive",
        "if=pflash,unit=1,format=raw,file=" + str(variables),
        "-chardev",
        "socket,id=tpmchar,path=" + str(control),
        "-tpmdev",
        "emulator,id=tpm0,chardev=tpmchar",
        "-device",
        "tpm-tis,tpmdev=tpm0",
        "-drive",
        "if=virtio,format=qcow2,cache=none,file=" + str(disk),
    ]
    if iso:
        command += ["-cdrom", str(iso), "-boot", "order=d"]
    return command


def boot(disk, log_path, *, iso=None, timeout=900):
    code = pathlib.Path("/usr/share/OVMF/OVMF_CODE_4M.fd")
    variables = pathlib.Path("/usr/share/OVMF/OVMF_VARS_4M.fd")
    if not code.is_file() or not variables.is_file():
        raise ValueError(
            "Expected Debian OVMF firmware is missing; no silent firmware downgrade"
        )
    with tempfile.TemporaryDirectory(prefix="scos-boot-") as tmp:
        tmp = pathlib.Path(tmp)
        state = tmp / "tpm"
        state.mkdir()
        shutil.copyfile(variables, tmp / "vars.fd")
        control = tmp / "swtpm.sock"
        qemu = None
        tpm = None
        try:
            tpm = subprocess.Popen(
                [
                    "swtpm",
                    "socket",
                    "--tpm2",
                    "--tpmstate",
                    "dir=" + str(state),
                    "--ctrl",
                    "type=unixio,path=" + str(control),
                    "--flags",
                    "not-need-init",
                ]
            )
            wait_path(control, tpm)
            command = qemu_command(disk, code, tmp / "vars.fd", control, iso)
            qemu = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            return monitor_guest(
                qemu, log_path, installing=iso is not None, timeout=timeout
            )
        finally:
            stop(qemu)
            stop(tpm)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=pathlib.Path)
    args = p.parse_args()
    output = args.output.resolve()
    require_inputs(output)
    logs = output / "tests"
    logs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scos-smoke-") as tmp:
        tmp = pathlib.Path(tmp)
        records = []
        for index in (1, 2):
            disk = tmp / ("clone" + str(index) + ".qcow2")
            subprocess.run(
                [
                    "qemu-img",
                    "create",
                    "-f",
                    "qcow2",
                    "-F",
                    "raw",
                    "-b",
                    str(output / "raw/sc-linux.raw"),
                    str(disk),
                ],
                check=True,
            )
            records.append(boot(disk, logs / ("raw-" + str(index) + ".log")))
        if records[0]["machine_id"] == records[1]["machine_id"]:
            raise ValueError("Two fresh clones generated the same machine ID")
        target = tmp / "installed.qcow2"
        subprocess.run(
            ["qemu-img", "create", "-f", "qcow2", str(target), "8G"], check=True
        )
        boot(
            target, logs / "iso-install.log", iso=output / "sc-linux.iso", timeout=1800
        )
        records.append(boot(target, logs / "installed-boot.log"))
        if len({r["machine_id"] for r in records}) != 3:
            raise ValueError(
                "Installed image did not receive an independent machine ID"
            )
    (logs / "smoke.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "checks": ["two-raw-clones", "iso-install", "installed-boot"],
                "records": records,
                "secure_boot_enforcement": "not-tested",
                "remote_attestation": "not-tested",
                "freeipa_enrollment": "not-tested",
            },
            indent=2,
        )
        + "\n"
    )
    print("RAW boots, unique machine IDs, ISO installation and installed boot passed.")


if __name__ == "__main__":
    main()
