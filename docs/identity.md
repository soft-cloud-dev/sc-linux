# FreeIPA identity and certificate trust

[Home](../README.md) · [Build](building.md) · [Install](installing.md)

## 1. Review your identity configuration

[`config/identity.json`](../config/identity.json) defines the exact server, DNS domain and Kerberos realm:

```json
{
  "server": "ipa.softcloud.dev",
  "domain": "ipa.softcloud.dev",
  "realm": "IPA.SOFTCLOUD.DEV"
}
```

Use lowercase fully qualified hostnames **below** this domain. Do not enroll a node using the IPA server's own hostname. DNS and Kerberos realm are independent explicit settings.

## 2. Import only a verified public CA

The repository includes a public CA and fingerprint. Confirm that the **DER SHA-256** fingerprint matches the CA supplied by your FreeIPA administrator through an independent trusted channel. The following command replaces the checked-in CA when necessary:

```sh
bash scripts/notebook.sh notebooks/trust.ipynb /secure/path/ipa-ca.crt --sha256 VERIFIED_DER_SHA256
make check
git add trust/ipa-ca.crt trust/ipa-ca.sha256
git commit -m "Update verified public IPA CA"
```

The notebook checks the fingerprint, CA constraint, validity period and absence of private-key material. Both committed files are public. Rotate the CA only through reviewed source changes and rebuilt images.

## 3. Enroll a running host

Provision a unique hostname and SSH key first. Then obtain a **host-scoped, one-time enrollment password** through your existing IPA administration process.

```sh
sudo scos-enroll node01.ipa.softcloud.dev
```

The installed command checks CA trust, identity, hostname, DNS/time readiness and partial enrollment state before invoking `ipa-client-install` with the native interactive `-W` prompt. It verifies the expected host configuration afterward.

The OTP must not be stored in Jupyter, environment variables, seed media or build scripts. A successful enrollment is **not** itself an authorization or attestation decision.

## 4. Verify permissions in your real environment

Test allowed and denied SSH access (HBAC), sudo permissions, keytab identity, offline handling and revocation against your actual IPA policy. Build-time checks cannot establish these outcomes.

**Not implemented:** automatic host admission, OTP brokering gated by TPM attestation, or a remote verifier.
