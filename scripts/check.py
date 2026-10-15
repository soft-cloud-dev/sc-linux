#!/usr/bin/env python3
"""Check source inputs; use --require-trust before building images."""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from scos.core import check_tree, read_identity, verify_ca


def check_configuration() -> None:
    read_identity(ROOT / "config/identity.json")
    configuration = json.loads((ROOT / "config/build.json").read_text())
    if not re.fullmatch(r"\d{8}T\d{6}Z", configuration["snapshot"]):
        raise ValueError("Invalid Debian snapshot")
    if (
        configuration["release"] != "trixie"
        or configuration["mkosi_package"] != "25.3-7"
    ):
        raise ValueError("Review the toolchain before changing its baseline")


def check_trust(required: bool) -> None:
    certificate = ROOT / "trust/ipa-ca.crt"
    fingerprint = ROOT / "trust/ipa-ca.sha256"
    if not required and not certificate.exists() and not fingerprint.exists():
        print(
            "IPA CA not configured. Source checks are available; image builds are blocked."
        )
        return
    if not certificate.is_file() or not fingerprint.is_file():
        raise ValueError(
            "Add the real IPA CA with scripts/trust.py; no placeholder CA is accepted"
        )
    verify_ca(certificate, fingerprint.read_text())


def check_actions() -> None:
    for workflow in (ROOT / ".github/workflows").glob("*.yml"):
        for action in re.findall(r"uses:\s*([^\s]+)", workflow.read_text()):
            if not re.fullmatch(r"[\w.-]+/[\w./-]+@[a-f0-9]{40}", action):
                raise ValueError("Unpinned action: " + action)


def check_python_syntax() -> None:
    """Parse host tools and extensionless guest commands without running them."""
    files = [
        *ROOT.glob("lib/**/*.py"),
        *ROOT.glob("scripts/*.py"),
        *ROOT.glob("tests/*.py"),
    ]
    for command in ROOT.glob("images/*/overlay/usr/local/sbin/*"):
        if command.is_file() and "python" in command.read_text().splitlines()[0]:
            files.append(command)
    for path in files:
        ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-trust", action="store_true")
    arguments = parser.parse_args()
    check_configuration()
    for image in ("server", "installer"):
        check_tree(ROOT / "images" / image / "overlay")
    check_trust(arguments.require_trust)
    check_actions()
    check_python_syntax()
    print("Source checks passed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, SyntaxError) as error:
        sys.exit(str(error))
