.DEFAULT_GOAL := help
.PHONY: help check builder images smoke repro lab

help:
	@printf '%s\n' \
	  'SC Linux image factory' \
	  '' \
	  '  make check    Run unit tests, source checks, and shell syntax checks' \
	  '  make lab      Open JupyterLab working copies' \
	  '  make builder  Build the pinned Docker toolchain' \
	  '  make images   Build the RAW disk and UEFI installer ISO' \
	  '  make smoke    Boot RAW clones, install the ISO, and boot the result' \
	  '  make repro    Compare two fresh unsigned builds byte for byte' \
	  '' \
	  'Start with README.md and docs/building.md.'

check:
	python3 -m unittest discover -s tests -v
	bash scripts/notebook.sh notebooks/check.ipynb
	@set -e; for script in scripts/*.sh; do bash -n "$$script"; done
	sh -n images/server/mkosi.finalize.chroot
	sh -n images/installer/mkosi.finalize.chroot
	sh -n images/installer/overlay/usr/local/sbin/scos-installer-shell

builder:
	bash scripts/builder.sh

images:
	bash scripts/build.sh

smoke:
	bash scripts/smoke.sh

repro:
	bash scripts/repro.sh

lab:
	bash scripts/lab.sh
