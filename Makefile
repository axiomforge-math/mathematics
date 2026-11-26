# AxiomForge archive — convenience targets (each result also documents its own
# reproduction commands; nothing here is required to reproduce a result).
#
#   make check                  validate every result (metadata, files, gates; no builds)
#   make catalogue              regenerate catalogue/ from results/*/result.toml
#   make catalogue-check        fail if catalogue/ is stale
#   make verify  RESULT=AF-0001 check + Lean build and axiom audit + manuscript build
#   make isolate RESULT=AF-0001 verify a copy of the result in a fresh temporary directory
#   make lean    RESULT=AF-0001 Lean build and axiom audit only
#   make paper   RESULT=AF-0001 manuscript build and layout checks only
#   make test                   run the archive tool's test suite

PYTHON ?= python3
AFM := $(PYTHON) scripts/afm.py

.PHONY: help check catalogue catalogue-check verify isolate lean paper test require-result

help:
	@sed -n '1,12p' Makefile | sed 's/^# \{0,1\}//'

check:
	$(AFM) check

catalogue:
	$(AFM) catalogue

catalogue-check:
	$(AFM) catalogue --check

require-result:
	@test -n "$(RESULT)" || (echo "usage: make $(MAKECMDGOALS) RESULT=AF-NNNN" && exit 2)

verify: require-result
	$(AFM) verify $(RESULT)

isolate: require-result
	$(AFM) isolate $(RESULT)

lean: require-result
	$(AFM) lean $(RESULT)

paper: require-result
	$(AFM) paper $(RESULT)

test:
	$(PYTHON) -m pytest -q tests
