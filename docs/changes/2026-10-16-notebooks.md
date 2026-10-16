# Notebook-first source migration — 2026-10-16

## What changed

Eight host-side Python operations moved from `scripts/*.py` to executable `notebooks/*.ipynb`. The notebook cells are the canonical implementation, not a wrapper that imports deleted scripts. A Python-standard-library runner (`scripts/notebook.sh`) runs those same cells inside Docker and in CI, without requiring an interactive Jupyter server.

Four guided notebooks provide the teaching sequence: validate, build, inspect and smoke-test. The README, build, install, identity, architecture, footprint, verification and contributor guides have been rewritten for that sequence.

Existing shell orchestration, installed guest commands, shared runtime Python library, artifact filenames, and test contracts are retained. The test suite now imports notebook code for its unit checks. The builder includes `dosfstools` and `mtools`, required by the ISO assembly operation.

## Limits

The migration does not prove successful OS image creation, VM boots, FreeIPA enrollment or reproducibility. Those require independent execution of the appropriate workflows. Runtime Python stays in the installed image; Jupyter does not.

The previous [readability rewrite record](2026-10-16-readability.md) describes an earlier repository state and must not be read as evidence for this migration.

## Interactive execution

`make lab` opens ignored working copies in `build/notebooks/`. This avoids Jupyter autosave changing tracked notebooks while the image builder enforces a clean Git checkout. The notebook setup cells locate the source repository from nested working directories.
