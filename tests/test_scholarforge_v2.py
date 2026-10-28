"""Offline unit tests for the 1.1.0 additions (spec, integrity, search log,
guidelines, disclosure, v2 sources). No network, no third-party packages."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# A lean `install.sh` copy deliberately omits build tools and upstream archives.
FULL_REPO = ((ROOT / "tools/validate_skill.py").is_file()
             and (ROOT / "upstream/v2/manifest.json").is_file())

from sf import (audit, disclosure, guidelines, integrity, searchlog,  # noqa: E402
                sources, spec)
from sf.util import read_json, write_json, write_text  # noqa: E402


class SpecTests(unittest.TestCase):
    def test_installed_skill_is_compliant(self):
        rep = spec.validate()
        self.assertTrue(rep["ok"], json.dumps([c for c in rep["checks"] if not c["ok"]], indent=2))

    def test_description_within_limit(self):
        fm = spec.frontmatter((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertLessEqual(len(fm["description"]), 1024)
        self.assertGreater(len(fm["description"]), 200)

    def test_metadata_values_are_strings(self):
        fm = spec.frontmatter((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        for k, v in fm["metadata"].items():
            self.assertIsInstance(v, str, f"metadata.{k}")

    def test_bad_directory_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "wrong-folder-name"
            p.mkdir()
            (p / "SKILL.md").write_text(
                '---\nname: scholar-forge\ndescription: "A test skill."\n---\n# Body\n',
                encoding="utf-8")
            for folder in ("scripts", "templates", "config"):
                (p / folder).mkdir()
            (p / "references").mkdir()
            self.assertFalse(spec.validate(p)["ok"])

    def test_reference_paths_resolve(self):
        rep = spec.validate()
        check = next(c for c in rep["checks"] if c["name"] == "referenced paths resolve")
        self.assertTrue(check["ok"], check["detail"])


class IntegrityTests(unittest.TestCase):
    def test_title_markers(self):
        s = integrity.title_signals("RETRACTED: Ileal-lymphoid-nodular hyperplasia")
        self.assertIn("title:retracted", s)

    def test_eoc_title_marker(self):
        s = integrity.title_signals("Expression of Concern: some study")
        self.assertIn("title:expression-of-concern", s)

    def test_two_signals_are_blocking(self):
        c = integrity.classify(["openalex:is_retracted", "crossref:retraction"], [], True)
        self.assertEqual(c["verdict"], "retracted-confirmed")
        self.assertTrue(c["blocking"])

    def test_single_signal_is_only_suspected(self):
        c = integrity.classify(["openalex:is_retracted"], [], True)
        self.assertEqual(c["verdict"], "retracted-suspected")
        self.assertFalse(c["blocking"])

    def test_correction_is_not_a_retraction(self):
        c = integrity.classify([], [{"type": "correction"}], True)
        self.assertEqual(c["verdict"], "notice-found")
        self.assertFalse(c["blocking"])

    def test_offline_check_is_deterministic(self):
        rep = integrity.check([{"id": "a", "title": "Normal paper", "doi": "10.1000/abc"}],
                              online=False)
        self.assertTrue(rep["summary"]["pass"])
        self.assertEqual(rep["results"][0]["verdict"], "not-checked")

    def test_offline_title_marker_blocks(self):
        rep = integrity.check([{"id": "a", "title": "RETRACTED: a study", "doi": ""}], online=False)
        self.assertFalse(rep["summary"]["pass"])
        self.assertEqual(rep["summary"]["blocking"], 1)

    def test_invalid_doi_does_not_hit_network(self):
        r = integrity.check_record({"id": "x", "title": "X", "doi": "not-a-doi"}, online=True)
        self.assertIn("invalid-doi", r["signals"])

    def test_report_contains_caveats(self):
        rep = integrity.check([], online=False)
        md = integrity.to_markdown(rep)
        self.assertIn("OpenAlex", md)
        self.assertIn("Limites", md)

    def test_audit_has_g_integrity_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / ".scholarforge").mkdir()
            (p / "sources").mkdir()
            write_text(p / "references.bib",
                       '@article{a,title={RETRACTED: a study},author={X},year={1998},doi={10.1000/a}}')
            rep = audit.run(p)
            names = [g["gate"] for g in rep["gates"]]
            self.assertIn("G-integrity", names)
            g = next(x for x in rep["gates"] if x["gate"] == "G-integrity")
            self.assertEqual(g["status"], "fail")
            self.assertTrue((p / "output/integrity.md").is_file())


class SourceFilterTests(unittest.TestCase):
    def test_normalise_coerces_ints(self):
        f = sources.normalise_filters({"from_year": "2020", "to_year": 2026,
                                      "min_citations": "5", "oa_only": True})
        self.assertEqual(f["from_year"], 2020)
        self.assertEqual(f["to_year"], 2026)
        self.assertEqual(f["min_citations"], 5)
        self.assertTrue(f["oa_only"])

    def test_normalise_rejects_bad_int(self):
        with self.assertRaises(ValueError):
            sources.normalise_filters({"from_year": "not-a-year"})

    def test_normalise_rejects_inverted_range(self):
        with self.assertRaises(ValueError):
            sources.normalise_filters({"from_year": 2030, "to_year": 2020})

    def test_apply_filters_year_and_citations(self):
        rows = [{"year": "2019", "cited_by": 100}, {"year": "2024", "cited_by": 1},
                {"year": "2024", "cited_by": 50}, {"year": "", "cited_by": None}]
        kept, applied = sources.apply_filters(rows, {"from_year": 2020, "min_citations": 10})
        self.assertEqual(len(kept), 2)
        self.assertTrue(any("from_year" in x for x in applied))

    def test_native_openalex_filter(self):
        extra, applied = sources.server_filters(
            "openalex", {"from_year": 2020, "to_year": 2026, "oa_only": True,
                         "min_citations": 10, "type": "article"})
        self.assertIn("from_publication_date:2020-01-01", extra["filter"])
        self.assertIn("is_oa:true", extra["filter"])
        self.assertIn("cited_by_count:>9", extra["filter"])
        self.assertEqual(len(applied), 5)

    def test_unknown_source_is_fail_soft_with_filters(self):
        rep = sources.search_all("x", ["not-a-real-source"], limit=1,
                                 filters={"from_year": 2020})
        self.assertEqual(rep["total_hits"], 0)
        self.assertEqual(rep["unique_hits"], 0)
        self.assertIn("filters", rep)

    def test_search_all_filters_are_not_shadowed(self):
        # Regression: a loop variable used to overwrite the normalised filter dict.
        rep = sources.search_all("x", ["not-a-real-source"], limit=1,
                                 filters={"from_year": 2022})
        self.assertIsInstance(rep["filters"], dict)
        self.assertEqual(rep["filters"]["from_year"], 2022)


class SearchLogTests(unittest.TestCase):
    def _report(self):
        return {"query": "RNA velocity", "retrieved_at": "2026-10-28T00:00:00+00:00",
                "unique_hits": 3, "filters": {"from_year": 2020},
                "filters_applied": {"openalex": {"applied": ["from_year=2020"], "ignored": []}},
                "sources": {"openalex": {"count": 3, "ok": True, "error": "",
                                         "url": "https://api.openalex.org/works?search=x"}}}

    def test_append_creates_markdown_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            res = searchlog.append(p, self._report(), {"from_year": 2020}, "1.1.0")
            self.assertEqual(res["rows_added"], 1)
            self.assertTrue((p / "sources/search-log.md").is_file())
            self.assertTrue((p / "sources/search-log.json").is_file())
            self.assertIn("Requested filters", (p / "sources/search-log.md").read_text())

    def test_append_is_cumulative(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            searchlog.append(p, self._report(), {"from_year": 2020}, "1.1.0")
            searchlog.append(p, self._report(), {"from_year": 2020}, "1.1.0")
            self.assertEqual(len(searchlog.read(p)), 2)
            s = searchlog.summary(p)
            self.assertEqual(s["queries"], 2)
            self.assertTrue(s["complete"])

    def test_entries_carry_provenance(self):
        e = searchlog.entries_from_report(self._report(), {"from_year": 2020}, "1.1.0")[0]
        for k in ("date_utc", "database", "query", "filters", "hits", "endpoint", "cli_version"):
            self.assertIn(k, e)
        self.assertEqual(e["filters"], "from_year=2020")


class GuidelineTests(unittest.TestCase):
    def test_catalogue_has_ai_guidelines(self):
        rows = {r["key"]: r for r in guidelines.catalogue()}
        self.assertGreaterEqual(len(rows), 18)
        self.assertEqual(rows["prediction-model"]["year"], 2024)
        self.assertEqual(rows["diagnostic-accuracy"]["year"], 2025)
        self.assertTrue(rows["ai-trial-report"]["ai_specific"])

    def test_tripod_supersedes_2015(self):
        c = guidelines.checklist("prediction-model")
        self.assertIn("TRIPOD 2015", c["supersedes"])
        self.assertIn("official statement", guidelines.to_markdown(c).lower())

    def test_checklist_markdown_has_boxes(self):
        md = guidelines.to_markdown(guidelines.checklist("systematic-review", "T", "V"))
        self.assertIn("| [ ] |", md)
        self.assertIn("Before submission", md)

    def test_recommend_diagnostic_ai(self):
        rec = guidelines.recommend("diagnostic accuracy of an AI test")
        self.assertIn("diagnostic-accuracy", [r["key"] for r in rec])

    def test_unknown_guideline_raises(self):
        with self.assertRaises(ValueError):
            guidelines.checklist("does-not-exist")

    def test_disclosure_lint_good_and_bad(self):
        good = ("We used Claude Sonnet (version 4.5, accessed 2026-10-28) for the purpose of "
                "language editing. A human reviewed and verified all content and takes full "
                "responsibility. AI cannot be an author.")
        self.assertTrue(guidelines.lint_disclosure(good)["summary"]["pass"])
        self.assertFalse(guidelines.lint_disclosure("")["summary"]["pass"])


class DisclosureTests(unittest.TestCase):
    def test_generate_and_lint(self):
        d = disclosure.generate(tool="Claude", version="2026-10-28",
                                purposes=["search", "writing", "editing"],
                                oversight="Named author", verification="Crossref",
                                prompts="Annex B", authors="Named author", policy_date="2026-10-28")
        self.assertEqual(len(d["categories"]), 3)
        md = disclosure.to_markdown(d)
        self.assertIn("Delegation table", md)
        self.assertIn("CRediT", md)
        self.assertTrue(disclosure.lint(md)["summary"]["pass"])

    def test_unknown_category_raises(self):
        with self.assertRaises(ValueError):
            disclosure.generate(purposes=["telepathy"])

    def test_categories_are_nine(self):
        self.assertEqual(len(disclosure.categories()), 9)


class V2AssetTests(unittest.TestCase):
    def test_28_references(self):
        self.assertEqual(len(list((ROOT / "references").glob("*.md"))), 28)

    @unittest.skipUnless(FULL_REPO, "lean install: build artefacts intentionally absent")
    def test_v2_manifest(self):
        m = read_json(ROOT / "upstream/v2/manifest.json", {})
        self.assertEqual(len(m.get("repositories", {})), 6)
        self.assertIn("CURATED", m["policy"])

    def test_scan_v2_summary(self):
        s = read_json(ROOT / "data/scan-v2-summary.json", {})
        self.assertEqual(s["repositories"], 6)
        self.assertGreater(s["files"], 1000)

    def test_registry_extended(self):
        d = read_json(ROOT / "data/registry.json", {})
        self.assertGreater(d["count"], 5434)
        self.assertTrue(any(e["id"].startswith("v2-") for e in d["entries"]))

    @unittest.skipUnless(FULL_REPO, "lean install: build artefacts intentionally absent")
    def test_research_notes_and_scan_report_v2_exist(self):
        self.assertTrue((ROOT / "docs/RESEARCH_NOTES.md").is_file())
        self.assertTrue((ROOT / "docs/SCAN_REPORT_V2.md").is_file())
        self.assertTrue((ROOT / "tools/validate_skill.py").is_file())

    def test_cli_version(self):
        from sf import cli
        self.assertEqual(cli.__version__, "1.1.0")
        import argparse
        parser = cli.build_parser()
        sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
        cmds = set(sub.choices)
        for c in ("integrity", "guideline", "disclosure", "searchlog", "validate"):
            self.assertIn(c, cmds)


if __name__ == "__main__":
    unittest.main()
