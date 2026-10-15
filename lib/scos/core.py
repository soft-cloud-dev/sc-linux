"""Small, dependency-free validation helpers shared by build and enrollment."""

import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess


def read_identity(path):
    """Read the explicit server, DNS domain, and Kerberos realm contract."""
    data = json.loads(pathlib.Path(path).read_text())
    if set(data) != {"server", "domain", "realm"}:
        raise ValueError("Identity must explicitly contain server, domain and realm")
    for key in ("server", "domain"):
        value = data[key]
        if not isinstance(value, str) or len(value) > 253 or value != value.lower():
            raise ValueError("Invalid " + key)
        if len(value.split(".")) < 2 or any(
            not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p)
            for p in value.split(".")
        ):
            raise ValueError("Invalid " + key)
    if not isinstance(data["realm"], str) or not re.fullmatch(
        r"[A-Z0-9][A-Z0-9.-]{0,252}", data["realm"]
    ):
        raise ValueError("An explicit, uppercase Kerberos realm is required")
    return data


def validate_hostname(name, domain):
    """Require a lowercase client FQDN strictly below the configured domain."""
    if not isinstance(name, str) or len(name) > 253 or not name.endswith("." + domain):
        raise ValueError("Host must be an explicit FQDN below " + domain)
    if any(
        not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p)
        for p in name.split(".")
    ):
        raise ValueError("Invalid hostname")
    return name


def _openssl(*args):
    try:
        return subprocess.check_output(
            ["openssl", *map(str, args)], stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise ValueError("OpenSSL rejected certificate input") from e


def certificate_fingerprint(path):
    """Hash the certificate DER bytes, independent of PEM formatting."""
    return hashlib.sha256(_openssl("x509", "-in", path, "-outform", "DER")).hexdigest()


def verify_ca(path, expected):
    """Reject wrong fingerprints, private keys, non-CA and expired certificates."""
    path = pathlib.Path(path)
    expected = expected.strip().replace(":", "").lower()
    if not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("Supply the independently verified CA DER SHA-256 fingerprint")
    raw = path.read_bytes()
    if b"PRIVATE KEY" in raw or raw.count(b"-----BEGIN CERTIFICATE-----") != 1:
        raise ValueError(
            "Expected exactly one public CA certificate and no private key"
        )
    actual = certificate_fingerprint(path)
    if actual != expected:
        raise ValueError("CA fingerprint mismatch")
    if b"CA:TRUE" not in _openssl(
        "x509", "-in", path, "-noout", "-ext", "basicConstraints"
    ):
        raise ValueError("Certificate is not a CA")
    dates = (
        _openssl("x509", "-in", path, "-noout", "-startdate", "-enddate")
        .decode()
        .splitlines()
    )
    parsed = [
        dt.datetime.strptime(line.split("=", 1)[1], "%b %d %H:%M:%S %Y %Z").replace(
            tzinfo=dt.timezone.utc
        )
        for line in dates
    ]
    now = dt.datetime.now(dt.timezone.utc)
    if not parsed[0] <= now < parsed[1]:
        raise ValueError("CA certificate is not currently valid")
    return actual


def enrollment_command(identity, hostname, ca):
    """Build the native client command; obtain its OTP only through the prompt."""
    validate_hostname(hostname, identity["domain"])
    if hostname == identity["server"]:
        raise ValueError("Do not enroll a client using the IPA server hostname")
    return [
        "ipa-client-install",
        "--hostname=" + hostname,
        "--server=" + identity["server"],
        "--domain=" + identity["domain"],
        "--realm=" + identity["realm"],
        "--ca-cert-file=" + str(ca),
        "--fixed-primary",
        "--mkhomedir",
        "--no-ntp",
        "--no-krb5-offline-passwords",
        "-W",
    ]


def describe_file(path):
    """Stream a regular artifact into a SHA-256 and byte-count manifest."""
    path = pathlib.Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise ValueError("Missing, empty, nonregular or symlink artifact: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"size": path.stat().st_size, "sha256": digest.hexdigest()}


def verify_file(path, expected):
    """Require an exact manifest match before consuming an artifact."""
    if set(expected) != {"size", "sha256"} or describe_file(path) != expected:
        raise ValueError("Artifact size or digest mismatch: " + str(path))


def check_tree(root):
    """Reject machine-specific state and private keys in an image filesystem."""
    root = pathlib.Path(root)
    forbidden = (
        "etc/krb5.keytab",
        "etc/ipa/default.conf",
        "etc/ssh/ssh_host_*",
        "root/.ssh/authorized_keys",
        "var/lib/systemd/random-seed",
        "var/lib/cloud/instances/*",
        "var/lib/sss/db/*",
    )
    for pattern in forbidden:
        if list(root.glob(pattern)):
            raise ValueError("Machine-specific state found: " + pattern)
    for name in ("etc/machine-id", "var/lib/dbus/machine-id"):
        p = root / name
        if (
            p.is_file()
            and not p.is_symlink()
            and p.read_text().strip() not in ("", "uninitialized")
        ):
            raise ValueError("Baked machine ID found")
    for subdir in ("etc", "root"):
        for p in (root / subdir).rglob("*"):
            if p.is_file() and not p.is_symlink() and p.stat().st_size < 1024 * 1024:
                if re.search(
                    rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----", p.read_bytes()
                ):
                    raise ValueError(
                        "Private key found in image: " + str(p.relative_to(root))
                    )
