#!/usr/bin/env python3
"""Offline unit tests for the ScholarForge runtime. No network, no dependencies."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sf import audit, bib, claims, lint, pipeline, prisma, registry, review, scaffold, sources, verify  # noqa: E402
from sf.cli import main  # noqa: E402


BIB = """@article{Smith2020,
  author = {Smith, Jane and Doe, Richard},
  title = {A {Nested} Title with Braces},
  journal = {Journal of Testing},
  year = {2020},
  volume = {12},
  number = {3},
  pages = {1--10},
  doi = {10.1234/example.2020}
}
@inproceedings{Lee2021,
  author = {Lee, A.},
  title = {A {Nested} Title with Braces},
  booktitle = {Proc. of Tests},
  year = {2021}
}
"""

RIS = """TY  - JOUR
TI  - A reproducible study
AU  - Smith, Jane
AU  - Doe, Richard
PY  - 2022/05/01
JO  - Journal of Testing
DO  - 10.5555/repro.2022
ER  -
"""

SLOPPY = (
    "# Introduction\n\n"
    "It is important to note that this field plays a pivotal role in today's fast-paced world. "
    "We delve into a rich tapestry of ideas in order to shed light on a paradigm shift. "
    "TODO: add citations. [citation needed] This is not only novel but also very significant. "
    "The results may possibly suggest that something could happen.\n\n"
    "# Methods\n\n# Results\n\n# Discussion\n"
)

CLEAN = (
    "# Introduction\n\n"
    "Prior work measured recall on three corpora (Smith, 2020). We ask whether the effect holds "
    "for low-resource languages.\n\n"
    "# Methods\n\n"
    "We evaluated 12 systems on 4 datasets. The primary outcome was macro-F1 with bootstrap "
    "confidence intervals.\n\n"
    "# Results\n\n"
    "System A reached 0.71 (95% CI 0.68-0.74) versus 0.65 for the baseline. The difference "
    "was 0.06 (95% CI 0.02-0.10).\n\n"
    "# Discussion\n\n"
    "The gain is modest. One limitation is the small number of corpora; the confidence interval "
    "includes effects below the pre-specified threshold.\n"
)


class TestBib(unittest.TestCase):
    def test_parse_bib_nested(self):
        recs = bib.parse_bib(BIB)
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0]["author"], "Smith, Jane and Doe, Richard")
        self.assertEqual(recs[0]["title"], "A {Nested} Title with Braces")
        self.assertEqual(recs[0]["doi"], "10.1234/example.2020")

    def test_parse_ris(self):
        recs = bib.parse_ris(RIS)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["year"], "2022")
        self.assertIn("Smith", recs[0]["author"])
        self.assertIn("Doe", recs[0]["author"])

    def test_parse_any_autodetect(self):
        self.assertEqual(len(bib.parse_any(BIB)), 2)
        self.assertEqual(len(bib.parse_any(RIS)), 1)
        self.assertEqual(bib.parse_any("nothing useful"), [])

    def test_dedupe(self):
        recs = bib.parse_bib(BIB)
        kept, dups = bib.dedupe(recs)
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0]["reason"], "fuzzy-title")
        self.assertEqual(kept[0].get("booktitle"), "Proc. of Tests")

    def test_styles(self):
        rec = bib.parse_bib(BIB)[0]
        for style in ("apa", "ieee", "vancouver", "chicago"):
            s = bib.format_ref(rec, style)
            self.assertTrue(len(s) > 30)
            self.assertIn("2020", s)

    def test_problems(self):
        self.assertIn("missing-title", bib.detect_problems({"author": "X", "year": "2020"}))
        self.assertIn("malformed-doi", bib.detect_problems(
            {"title": "T", "author": "A", "year": "2020", "doi": "not-a-doi"}))
        self.assertIn("placeholder-text", bib.detect_problems(
            {"title": "TODO fill in", "author": "A", "year": "2020"}))

    def test_bibtex_roundtrip(self):
        rec = bib.parse_bib(BIB)[0]
        again = bib.parse_bib(bib.to_bibtex(rec))
        self.assertEqual(len(again), 1)
        self.assertEqual(again[0]["title"], rec["title"])


class TestVerify(unittest.TestCase):
    def test_offline_statuses(self):
        recs = bib.parse_bib(BIB)
        rep = verify.verify(recs, online=False)
        self.assertEqual(rep["summary"]["total"], 2)
        self.assertFalse(rep["summary"]["online"])
        self.assertIn("doi-present-unchecked", rep["summary"]["counts"])
        self.assertTrue(any(r["status"] == "needs-review" for r in rep["results"]))

    def test_invalid_doi_format(self):
        r = sources.verify_doi("this-is-not-a-doi")
        self.assertEqual(r["status"], "invalid-format")
        self.assertIsNone(r["crossref"])

    def test_markdown_report(self):
        md = verify.to_markdown(verify.verify(bib.parse_bib(BIB)))
        self.assertIn("Rapport de vérification", md)
        self.assertTrue("PASS" in md or "FAIL" in md)


class TestPrisma(unittest.TestCase):
    def _rows(self, final="include"):
        return [
            {"id": "R1", "source": "OpenAlex", "stage": "ta", "title": "A",
             "r1": "include", "r2": "include", "adjudicated": "", "exclusion_code": ""},
            {"id": "R2", "source": "PubMed", "stage": "ta", "title": "B",
             "r1": "exclude", "r2": "exclude", "adjudicated": "", "exclusion_code": "E3-wrong-population"},
            {"id": "R3", "source": "OpenAlex", "stage": "ft", "title": "C",
             "r1": final, "r2": final, "adjudicated": "", "exclusion_code": ""},
        ]

    def test_valid_report(self):
        rep = prisma.report(self._rows())
        self.assertTrue(rep["pass"], rep["issues"])
        self.assertEqual(rep["counts"]["records_identified"], 3)
        self.assertEqual(rep["counts"]["studies_included"], 2)
        self.assertIn("mermaid", rep["flow_mermaid"])
        self.assertEqual(rep["agreement"]["kappa"], 1.0)

    def test_unresolved_is_error(self):
        rep = prisma.report(self._rows(final="unclear"))
        self.assertFalse(rep["pass"])
        self.assertTrue(any(i["issue"].startswith("missing/ambiguous") for i in rep["issues"]))

    def test_disagreement_needs_adjudication(self):
        rows = self._rows()
        rows[1]["r2"] = "include"
        rep = prisma.report(rows)
        self.assertFalse(rep["pass"])
        self.assertTrue(any("adjudication" in i["issue"] for i in rep["issues"]))


class TestClaims(unittest.TestCase):
    def test_valid_ledger(self):
        c = [{"claim_id": "C1", "claim_text": "X may reduce Y in this sample.",
              "evidence_ids": "E1", "strength": "suggestive"}]
        e = [{"evidence_id": "E1", "source_id": "S1", "design": "rct", "stance": "supports"}]
        rep = claims.validate(c, e)
        self.assertTrue(rep["summary"]["pass"], rep["findings"])

    def test_dangling_and_placeholder(self):
        c = [{"claim_id": "C1", "claim_text": "X proves Y. [citation needed]",
              "evidence_ids": "E99", "strength": "established"}]
        e = [{"evidence_id": "E1", "source_id": "S1", "design": "case-report", "stance": "supports"}]
        rep = claims.validate(c, e)
        self.assertFalse(rep["summary"]["pass"])
        rules = " ".join(f["issue"] for f in rep["findings"])
        self.assertIn("dangling", rules)
        self.assertIn("placeholder", rules)


class TestLint(unittest.TestCase):
    def test_flags_slop(self):
        rep = lint.lint(SLOPPY)
        by = rep["summary"]["by_rule"]
        self.assertGreater(by.get("slop-phrase", 0), 3)
        self.assertGreaterEqual(by.get("placeholder", 0), 2)
        self.assertFalse(rep["summary"]["pass"])
        self.assertLess(rep["summary"]["score"], 70)

    def test_clean_passes(self):
        rep = lint.lint(CLEAN)
        self.assertTrue(rep["summary"]["pass"], rep["summary"])
        self.assertGreaterEqual(rep["summary"]["score"], 70)

    def test_readability(self):
        rd = lint.readability(CLEAN)
        self.assertGreater(rd["words"], 40)
        self.assertIsNotNone(rd["flesch"])


class TestReview(unittest.TestCase):
    def test_parse_comments(self):
        text = "R1C1: The sample size is not justified.\nR2C1: Please report confidence intervals."
        rows = review.parse_comments(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["comment_id"], "R1C1")

    def test_rebuttal_matrix(self):
        rows = review.rebuttal_matrix("R1C1: report p-values.\nR1C2: clarify the method.")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["status"] == "open" for r in rows))

    def test_review_lint(self):
        rep = review.lint_review("This is a short review that accepts the paper.")
        self.assertFalse(any(f["severity"] == "error" for f in rep["findings"]))


class TestProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "project"

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_and_templates(self):
        rep = scaffold.init_project(self.root, "Test study")
        self.assertTrue((self.root / "draft/manuscript.md").is_file())
        self.assertTrue((self.root / ".scholarforge/state.json").is_file())
        self.assertTrue((self.root / "review/peer-review-form.md").is_file())
        text = (self.root / "draft/manuscript.md").read_text(encoding="utf-8")
        self.assertNotIn("{{TITLE}}", text)
        self.assertIn("Test study", text)
        self.assertGreater(len(rep["files"]), 10)

    def test_new_template(self):
        p = scaffold.new("cover", self.root / "letter.md", TITLE="Hello", VENUE="Nature")
        self.assertTrue(p.is_file())
        self.assertIn("Hello", p.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            scaffold.new("does-not-exist", self.root / "x.md")

    def test_pipeline_state_machine(self):
        scaffold.init_project(self.root, "Test")
        s = pipeline.status(self.root)
        self.assertEqual(s["stage"], "S0")
        blocked = pipeline.advance("S2", self.root)
        self.assertFalse(blocked["ok"])
        forced = pipeline.advance("S2", self.root, force=True)
        self.assertTrue(forced["ok"])
        self.assertEqual(pipeline.status(self.root)["stage"], "S2")
        self.assertTrue(any(h.get("force") for h in pipeline.status(self.root)["history"]))
        pipeline.reset(self.root, "S1")
        self.assertEqual(pipeline.status(self.root)["stage"], "S1")

    def test_audit_runs(self):
        scaffold.init_project(self.root, "Test")
        rep = audit.run(self.root)
        self.assertIn(rep["verdict"], ("PASS", "FAIL"))
        self.assertTrue((self.root / "output/AUDIT.md").is_file())
        self.assertTrue((self.root / "output/lint.md").is_file())
        self.assertIn("limits", rep)


class TestRegistryAndCLI(unittest.TestCase):
    def test_registry_stats(self):
        s = registry.stats()
        self.assertGreater(s["total"], 1000)
        self.assertIn("discovery", s["by_stage"])

    def test_registry_search(self):
        r = registry.search("citation verification", limit=5)
        self.assertGreater(r["count"], 0)
        self.assertLessEqual(len(r["results"]), 5)

    def test_cli_doctor(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["doctor", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertTrue(data["ok"])
        self.assertGreater(data["references"], 15)

    def test_cli_selftest_discovery(self):
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_scholarforge.py")
        self.assertGreater(suite.countTestCases(), 15)

    def test_search_fails_soft_offline(self):
        rep = sources.search_all("irrelevant", ["not-a-real-source"], limit=1)
        self.assertFalse(rep["sources"]["not-a-real-source"]["ok"])
        self.assertEqual(rep["total_hits"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
