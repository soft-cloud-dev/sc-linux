#!/usr/bin/env python3
"""Install a public IPA CA only after checking an independently obtained fingerprint."""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from scos.core import verify_ca


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("certificate", type=pathlib.Path)
    p.add_argument(
        "--sha256",
        required=True,
        help="Independently verified SHA-256 of the DER certificate",
    )
    args = p.parse_args()
    digest = verify_ca(args.certificate, args.sha256)
    raw = args.certificate.read_bytes()
    (ROOT / "trust/ipa-ca.crt").write_bytes(raw)
    (ROOT / "trust/ipa-ca.sha256").write_text(digest + "\n")
    print(
        "Verified public CA installed. Review and commit trust/ipa-ca.crt and trust/ipa-ca.sha256."
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as e:
        sys.exit(str(e))
