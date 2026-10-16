# Public FreeIPA CA

This directory contains **only public trust material**. A fresh checkout has no active IPA CA until the operator installs the real certificate.

1. Obtain the public IPA CA certificate from your administrator.
2. Independently verify its **DER-encoded SHA-256** certificate fingerprint.
3. Run the [trust notebook](../notebooks/trust.ipynb) from the repository root:

```sh
bash scripts/notebook.sh notebooks/trust.ipynb /secure/path/ipa-ca.crt --sha256 VERIFIED_DER_SHA256
```

Review and commit the generated public `ipa-ca.crt` and `ipa-ca.sha256`. Never commit a private key, an enrollment OTP, or a placeholder certificate. Image builds refuse missing or invalid trust.
