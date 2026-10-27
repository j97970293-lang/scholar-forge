# ScholarForge — raccourcis reproductibles
SF := python3 scripts/scholarforge.py
SOURCES ?= ../_scan

.PHONY: help doctor test demo demo-fixed scan package compile clean lint

help:
	@echo "doctor | test | demo | demo-fixed | scan | package | compile | clean"

doctor:
	$(SF) doctor

test:
	$(SF) selftest

compile:
	python3 -m compileall -q scripts tools tests

demo:
	bash examples/end-to-end/run-demo.sh

demo-fixed:
	bash examples/end-to-end/run-demo.sh --fixed

scan:
	SF_SOURCES=$(SOURCES) python3 tools/scan_sources.py
	SF_SOURCES=$(SOURCES) python3 tools/security_scan.py
	python3 tools/merge_registry.py

package:
	SF_SOURCES=$(SOURCES) python3 tools/package_upstream.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
