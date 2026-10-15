# Repository readability rewrite

## Goal and scope

Make the supplied image factory easy to navigate, operate, and maintain.
Keep Debian 13, amd64, mkosi 25.3-7, the existing command names, artifact names,
and explicit FreeIPA identity. This is a source rewrite, not OS qualification.

## Design

- `images/server/` and `images/installer/` each own a recipe and filesystem overlay.
- `lib/scos/` owns Python validation shared by host tools and installed commands.
- `scripts/` owns host-side orchestration; `tests/` exercises its safety contracts.
- The README introduces the project. Task guides hold the operational details.
- Source checks remain usable without Docker, a real IPA CA, or an IPA server.

## Implementation plan

1. Relocate image inputs and shared helpers; update all consumers together.
2. Rewrite dense Python and shell into named operations with explicit entrypoints.
3. Rewrite documentation around building, installing, enrolling, and verifying.
4. Validate source, CLI help, staging, documentation links, and negative preflight.
5. Publish the verified source to `soft-cloud-dev/sc-linux` without force-pushing.

## Review focus

Moving a file must not omit it from an image. Importing a helper must not execute
its CLI. Installer checks must still run before a write. Enrollment credentials
must remain interactive. Documentation must distinguish source tests from actual
image builds, VM boots, and live enrollment.

## Baseline

The supplied archive passes 18 unit tests and its source/shell checks. It has no
real CA trust files. The destination was confirmed accessible with push permission.

## Verification result

The rewrite passes 23 tests, source and shell checks, documentation-link checks,
workflow YAML parsing, and Python formatting checks. An independent review found
no blocking rewrite regressions. The deliberate default-command change is that
bare `make` shows help; `make check` continues to run validation. Image and live
identity qualification remain pending as documented in [verification](../verification.md).
