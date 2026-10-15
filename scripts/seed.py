#!/usr/bin/env python3
"""Create a per-host NoCloud ISO containing a hostname and a public SSH key."""

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from scos.core import read_identity, validate_hostname


def user_data(hostname, public_key):
    return {
        "fqdn": hostname,
        "hostname": hostname.split(".")[0],
        "preserve_hostname": False,
        "manage_etc_hosts": True,
        "disable_root": True,
        "ssh_pwauth": False,
        "users": [
            {
                "name": "scos",
                "groups": ["sudo"],
                "shell": "/bin/bash",
                "lock_passwd": True,
                "sudo": ["ALL=(ALL) NOPASSWD:ALL"],
                "ssh_authorized_keys": [public_key],
            }
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("hostname")
    p.add_argument("public_key", type=pathlib.Path)
    p.add_argument("output", type=pathlib.Path)
    args = p.parse_args()
    identity = read_identity(ROOT / "config/identity.json")
    validate_hostname(args.hostname, identity["domain"])
    if args.hostname == identity["server"]:
        raise ValueError("The IPA server name is not a client hostname")
    key = args.public_key.read_text().strip()
    if "\n" in key or not key.startswith(("ssh-ed25519 ", "ssh-rsa ", "ecdsa-sha2-")):
        raise ValueError(
            "Supply one OpenSSH public key; not a private key or authorized_keys options"
        )
    subprocess.run(
        ["ssh-keygen", "-l", "-f", str(args.public_key)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    if args.output.exists():
        raise ValueError("Refusing to overwrite existing seed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scos-seed-") as tmp:
        stage = pathlib.Path(tmp)
        (stage / "user-data").write_text(
            "#cloud-config\n"
            + json.dumps(user_data(args.hostname, key), indent=2)
            + "\n"
        )
        (stage / "meta-data").write_text(
            json.dumps(
                {"instance-id": str(uuid.uuid4()), "local-hostname": args.hostname}
            )
            + "\n"
        )
        subprocess.run(
            [
                "xorriso",
                "-as",
                "mkisofs",
                "-quiet",
                "-V",
                "cidata",
                "-J",
                "-R",
                "-o",
                str(args.output.resolve()),
                str(stage),
            ],
            check=True,
        )
    print(args.output)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        sys.exit("seed: " + str(e))
