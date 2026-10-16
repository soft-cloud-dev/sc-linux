# Public FreeIPA CA

This directory contains **only public trust material**. The repository includes a public CA certificate and its DER SHA-256 fingerprint. **Their presence does not establish independent trust.** Confirm the fingerprint through your FreeIPA administrator before building; replace the pair when using a different CA.

1. Obtain the public IPA CA certificate from your administrator.
2. Independently verify its **DER-encoded SHA-256** certificate fingerprint.
3. Run the [trust notebook](../notebooks/trust.ipynb) from the repository root:

```sh
bash scripts/notebook.sh notebooks/trust.ipynb /secure/path/ipa-ca.crt --sha256 VERIFIED_DER_SHA256
```

Review and commit the generated public `ipa-ca.crt` and `ipa-ca.sha256`. Never commit a private key, an enrollment OTP, or a placeholder certificate. Image builds refuse missing or invalid trust.
