# ScholarForge — raccourcis reproductibles
SF := python3 scripts/scholarforge.py
SOURCES ?= ../_scan
SOURCES_V2 ?= ../_scan2

.PHONY: help doctor test validate demo demo-fixed scan v2 package release compile clean

help:
	@echo "doctor | test | validate | demo | demo-fixed | scan | v2 | package | release | compile | clean"

doctor:
	$(SF) doctor

test:
	$(SF) selftest

validate:
	python3 tools/validate_skill.py
	$(SF) validate

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

v2:
	python3 tools/v2_pipeline.py --sources $(SOURCES_V2)

package:
	SF_SOURCES=$(SOURCES) python3 tools/package_upstream.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete

release:
	python3 tools/package_release.py --output $(CURDIR)/..
