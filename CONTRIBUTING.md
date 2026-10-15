# Contributing

Start with the [architecture map](docs/architecture.md). Keep changes small enough
to explain their effect on the generated image or operator workflow.

## Where to make a change

| Change | Location |
| --- | --- |
| IPA server, DNS domain, or realm | `config/identity.json` |
| Snapshot or toolchain baseline | `config/build.json`, plus matching validation/build constraints |
| Server packages or boot settings | `images/server/mkosi.conf` |
| Installer packages or boot settings | `images/installer/mkosi.conf` |
| Installed files or systemd units | The relevant image's `overlay/` |
| Shared validation | `lib/scos/core.py` |
| Host commands | `scripts/` |
| User-facing instructions | README and the relevant `docs/` guide |

The distribution, architecture, release, and mkosi baseline also appear in image
recipes, the Dockerfile, or validation. They are review constraints, not arbitrary
runtime selectors. Update them together and qualify a new baseline with image tests.

## Code style

- Give each function one operation and a descriptive name.
- Use one statement per line. Keep validation and side effects easy to distinguish.
- Put Python command execution inside `main()` and guard the entrypoint.
- Keep imports side-effect free so tests can exercise helpers safely.
- Use Python's standard library for runtime code; avoid packaging machinery for
  these small installed scripts.
- Follow `.editorconfig`. Python is formatted with Black at 88 columns; Black is
  an optional development tool, not a build or runtime requirement.
- Comments should explain ordering, trust boundaries, or an unusual constraint.

## Validate changes

```sh
make check
```

This runs unit tests, configuration and Python syntax checks, pinned-action checks,
and shell syntax checks. Tests create temporary CA/key fixtures outside tracked
source and clean them up afterward.

For changes to image layout, packages, boot, installer behavior, or systemd units,
also build and run `make smoke` on a supported host. Use `make repro` for changes
that affect determinism. Record exactly which checks ran; never equate source
tests with boot or enrollment qualification.

New safety behavior needs a focused regression test. For structural refactors,
retain the existing contracts and test the integration points that moved.

## Security and generated files

Keep generated content under ignored `build/`. Do not commit host credentials,
private signing keys, seed media, VM state, or image artifacts. Public IPA CA
changes require independent fingerprint verification. Follow [SECURITY.md](SECURITY.md).

Source publication does not select a license for the original code. The owner
must choose one before offering license-based reuse or redistribution rights.
