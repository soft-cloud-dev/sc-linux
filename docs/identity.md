# Identity and trust

[README](../README.md) · [Build](building.md) · [Install](installing.md)

## Configure the IPA environment

[config/identity.json](../config/identity.json) is the single identity definition:

```json
{
  "server": "ipa.softcloud.dev",
  "domain": "ipa.softcloud.dev",
  "realm": "IPA.SOFTCLOUD.DEV"
}
```

The DNS domain and Kerberos realm are explicit. The code never derives a realm
from DNS, the hostname, or the CA. Review these values for your deployment before
building. A client hostname must be a lowercase FQDN below the configured domain
and must differ from the IPA server name.

## Establish CA trust

Obtain the actual public IPA CA and verify its DER SHA-256 fingerprint through
an independent, trusted administrative channel. Then use `scripts/trust.py` as
shown in the [build guide](building.md#1-configure-trust).

The helper accepts exactly one public CA certificate. It rejects a mismatched
fingerprint, private-key material, a non-CA certificate, or a certificate outside
its validity period. Review and commit:

- `trust/ipa-ca.crt`: the public certificate.
- `trust/ipa-ca.sha256`: its verified DER SHA-256 fingerprint.

The build stages the certificate at
`/usr/local/share/ca-certificates/scos-ipa.crt` and registers it with
`update-ca-certificates`. Enrollment checks its fingerprint and validity again.
A CA rotation requires an independently verified source change and rebuilt images.

## Enroll a provisioned host

Create the host and issue its one-time enrollment password through your existing
IPA administration process. The operator or an external admission system decides
whether the host is allowed to enroll.

Connect using the bootstrap SSH key and run:

```sh
sudo scos-enroll node01.ipa.softcloud.dev
```

The wrapper runs as root and serializes enrollment attempts. For a new enrollment it:

1. Validates identity, the requested hostname, and CA trust.
2. Rejects partial or foreign enrollment state.
3. Requires an interactive terminal and a synchronized clock.
4. Calls the native `ipa-client-install` with its `-W` password prompt.
5. Verifies the expected host principal using the host keytab and checks SSSD configuration.

Enter the **one-time host enrollment password**, not an IPA administrator password.
Do not put it in command arguments, environment variables, seed media, or CI secrets.
The enrollment process and root can still access that credential; the interactive
prompt prevents exposure through arguments and shell history, not through a
compromised operating system.

If IPA configuration already exists, the wrapper verifies the enrollment instead
of forcing a rejoin. Reconcile incomplete or conflicting state with the IPA
administrator before retrying.

## Verify authorization separately

A successful client installation does not prove your access policy. Test against
the real server:

- Allowed and denied SSH logins under HBAC policy.
- Intended sudo permissions.
- Offline behavior and credential revocation.
- The expected host principal and unique host keytab.

The image contains no enrollment password, administrator credential, host keytab,
or pre-generated SSH host private key. Those unique secrets are created on the
running host and persist there after enrollment.

## Attestation boundary

This repository has no admission broker and does not gate OTP issuance on a
remote TPM verdict. Measured-boot diagnostics and optional EFI signing are
separate controls. See [security boundaries](../SECURITY.md) and
[verification limits](verification.md).
