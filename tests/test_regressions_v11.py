"""Regression coverage for final v1.1 hardening. Fully offline, stdlib only."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from sf import audit, cli, disclosure, guidelines, integrity, searchlog, sources, spec
from sf.util import read_json, write_json, write_text


class SearchLogRegressions(unittest.TestCase):
    def report(self, query="first query"):
        return {"query": query, "retrieved_at": "2026-10-28T12:00:00+00:00",
                "unique_hits": 1, "sources": {"openalex": {"ok": True, "count": 1,
                "url": "https://api.openalex.org/works?search=" + query}},
                "filters_applied": {"openalex": {"native": ["from_year=2020 (native)"],
                "applied": ["from_year=2020"], "ignored": []}}}

    def test_markdown_keeps_both_queries(self):
        with tempfile.TemporaryDirectory() as d:
            searchlog.append(d, self.report("FIRST-QUERY"))
            searchlog.append(d, self.report("SECOND-QUERY"))
            md = (Path(d) / "sources/search-log.md").read_text()
            self.assertIn("FIRST-QUERY", md)
            self.assertIn("SECOND-QUERY", md)
            self.assertEqual(md.count("## How to report this"), 1)

    def test_full_query_and_endpoint_are_not_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            query = "full exact search " + "x" * 400 + "END-OF-QUERY"
            searchlog.append(d, self.report(query))
            md = (Path(d) / "sources/search-log.md").read_text()
            self.assertIn(query, md)
            self.assertIn("https://api.openalex.org/works?search=" + query, md)

    def test_native_filters_survive_logging(self):
        e = searchlog.entries_from_report(self.report())[0]
        self.assertEqual(e["filters_native"], ["from_year=2020 (native)"])
        self.assertEqual(e["count_scope"], "retrieved-window-after-filters")

    def test_corrupt_json_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sources/search-log.json"
            write_text(p, "BROKEN-JSON")
            with self.assertRaises(ValueError):
                searchlog.append(d, self.report())
            self.assertEqual(p.read_text(), "BROKEN-JSON")

    def test_wrong_history_schema_is_not_reset(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sources/search-log.json"
            write_text(p, '{"manual": "preserve"}')
            with self.assertRaises(ValueError):
                searchlog.append(d, self.report())
            self.assertIn("preserve", p.read_text())

    def test_manual_markdown_rows_are_retained(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sources/search-log.md"
            write_text(p, "# Manual log\n| manual source | manual query |\n")
            searchlog.append(d, self.report())
            self.assertIn("| manual source | manual query |", p.read_text())


class SourceAndCLIRegressions(unittest.TestCase):
    def test_unsupported_native_filters_are_explicit(self):
        row = {"title": "Study", "year": "2024", "is_oa": None}
        with patch.dict(sources._CLIENT, {"crossref": lambda *a: ("https://example.test", [row], "")}):
            r = sources.search("crossref", "x", filters={"from_year": 2020, "oa_only": True})
        self.assertIn("oa_only", r["filters_applied"]["ignored"])
        self.assertEqual(r["filters_applied"]["unknown_metadata"]["oa_only"], 1)
        self.assertEqual(r["retrieved_before_filters"], 1)

    def test_false_string_is_not_true(self):
        self.assertFalse(sources.normalise_filters({"oa_only": "false"})["oa_only"])

    def test_negative_citation_count_rejected(self):
        with self.assertRaises(ValueError):
            sources.normalise_filters({"min_citations": -1})

    def test_invalid_year_rejected(self):
        with self.assertRaises(ValueError):
            sources.normalise_filters({"from_year": -2020})

    def test_search_json_is_machine_readable_with_log_and_out(self):
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                cli.main(["search", "q", "--sources", "unknown-source", "--json",
                          "--log-path", d, "--out", str(Path(d) / "hits.json")])
            rep = json.loads(buf.getvalue())
            self.assertIn("sources", rep)

    def test_guideline_json_with_out_is_pure(self):
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                cli.main(["guideline", "--key", "prediction-model", "--json",
                          "--out", str(Path(d) / "check.md")])
            self.assertEqual(json.loads(buf.getvalue())["key"], "prediction-model")

    def test_ris_has_one_au_per_author(self):
        rep = {"query": "x", "sources": {}, "merged": [{"title": "Test", "author": "A; B"}],
               "unique_hits": 1, "total_hits": 1, "filters": {}}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "out.ris"
            with patch.object(sources, "search_all", return_value=rep), contextlib.redirect_stdout(io.StringIO()):
                cli.main(["search", "x", "--no-log", "--ris", str(path)])
            self.assertEqual(path.read_text().count("AU  - "), 2)


class IntegrityRegressions(unittest.TestCase):
    def records(self):
        return [{"id": "a", "title": "Normal study", "doi": "10.1234/a"}]

    def test_current_cache_matches(self):
        rows = self.records()
        self.assertTrue(integrity.cache_matches(integrity.check(rows), rows))

    def test_stale_cache_is_rejected(self):
        rows = self.records()
        report = integrity.check(rows)
        report["summary"]["generated_at"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        self.assertFalse(integrity.cache_matches(report, rows))

    def test_changed_bibliography_invalidates_cache(self):
        rows = self.records()
        report = integrity.check(rows)
        rows[0]["title"] = "RETRACTED: changed study"
        self.assertFalse(integrity.cache_matches(report, rows))

    def test_audit_recomputes_after_bibliography_change(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            refs = p / "references.bib"
            write_text(refs, "@article{a,title={Normal study},author={A},year={2020},doi={10.1234/a}}")
            audit.run(p)
            write_text(refs, "@article{a,title={RETRACTED: study},author={A},year={2020},doi={10.1234/a}}")
            result = audit.run(p)
            g = next(g for g in result["gates"] if g["gate"] == "G-integrity")
            self.assertEqual(g["status"], "fail")

    def test_duplicate_flags_are_not_corroboration(self):
        c = integrity.classify(["openalex:is_retracted", "openalex:is_retracted"], [], True)
        self.assertEqual(c["verdict"], "retracted-suspected")
        self.assertFalse(c["blocking"])

    def test_two_title_markers_are_one_family(self):
        c = integrity.classify(["title:retracted", "title:withdrawn"], [], False)
        self.assertEqual(c["verdict"], "retracted-suspected")

    def test_missing_doi_is_not_checked_not_clean(self):
        r = integrity.check_record({"title": "No DOI"}, online=True)
        self.assertEqual(r["verdict"], "not-checked")
        self.assertFalse(r["checked_online"])

    def test_invalid_doi_is_never_clean(self):
        with patch.object(integrity, "_get_json", side_effect=AssertionError("no network")):
            r = integrity.check_record({"doi": "not-a-doi"}, online=True)
        self.assertEqual(r["verdict"], "invalid-doi")
        self.assertFalse(r["checked_online"])

    def test_incoming_relation_is_retraction_signal(self):
        response = {"message": {"relation": {"is-retracted-by": [{"id": "10.1234/notice"}]}}}
        with patch.object(integrity, "_get_json", return_value=(True, response, "")):
            r = integrity.crossref_signal("10.1234/a")
        self.assertEqual(r["notices"][0]["type"], "retraction")

    def test_outgoing_update_does_not_retract_notice(self):
        response = {"message": {"update-to": [{"type": "retraction", "DOI": "10.1234/original"}]}}
        with patch.object(integrity, "_get_json", return_value=(True, response, "")):
            r = integrity.crossref_signal("10.1234/notice")
        self.assertEqual(r["notices"][0]["type"], "outgoing-update")
        self.assertNotIn(r["notices"][0]["type"], integrity.RETRACTION_TYPES)

    def test_current_registry_title_is_checked(self):
        oa = {"ok": True, "error": "", "url": "https://a.test", "is_retracted": False, "title": "Study"}
        cr = {"ok": True, "error": "", "url": "https://b.test", "notices": [], "title": "RETRACTED: Study"}
        with patch.object(integrity, "openalex_signal", return_value=oa), patch.object(integrity, "crossref_signal", return_value=cr):
            r = integrity.check_record({"title": "Study", "doi": "10.1234/a"}, online=True)
        self.assertIn("title:retracted", r["signals"])


class SpecAndDisclosureRegressions(unittest.TestCase):
    def test_unquoted_numbers_are_not_yaml_strings(self):
        fm = spec.frontmatter('---\nname: scholar-forge\ndescription: Test\nmetadata:\n  count: 123\n  flag: true\n---\n')
        self.assertIsInstance(fm["metadata"]["count"], int)
        self.assertIs(fm["metadata"]["flag"], True)

    def test_missing_skill_report_renders(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("FAIL", spec.to_markdown(spec.validate(Path(d))))

    def test_all_runtime_files_parse_with_python39_grammar(self):
        for path in (ROOT / "scripts").rglob("*.py"):
            ast.parse(path.read_text(), filename=str(path), feature_version=(3, 9))

    def test_incomplete_disclosures_fail(self):
        for text in ((ROOT / "templates/ai-disclosure.md").read_text(),
                     disclosure.to_markdown(disclosure.generate())):
            with self.subTest(text=text[:50]):
                self.assertFalse(disclosure.lint(text)["summary"]["pass"])

    def test_complete_disclosure_passes_without_warning(self):
        text = disclosure.to_markdown(disclosure.generate(tool="Example model", version="1.0",
            purposes=["editing"], oversight="Human reviewed all edits", verification="Compared to source",
            prompts="Appendix B", title="Study", venue="Venue", authors="Named author", policy_date="2026-10-28"))
        report = disclosure.lint(text)
        self.assertTrue(report["summary"]["pass"], report)
        self.assertEqual(report["summary"]["warnings"], 0)

    def test_no_use_and_acknowledgement_are_not_ai_authorship(self):
        self.assertTrue(disclosure.lint("No generative AI tools were used in this work.")["summary"]["pass"])
        text = ("We thank Claude (version 4.5) for the purpose of editing. "
                "Human authors reviewed all content and take responsibility. AI tools are not authors.")
        self.assertTrue(guidelines.lint_disclosure(text)["summary"]["pass"])


if __name__ == "__main__":
    unittest.main()
