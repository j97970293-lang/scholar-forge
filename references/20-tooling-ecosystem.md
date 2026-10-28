# 20 — Tooling ecosystem and the merged registry

## What the registry is
`data/registry.json` merges every catalogue found in the eight v1 source repositories into
5,434 de-duplicated entries, plus 26 official/tool entries from the six v2 sources
(**5,460 in 1.1.0**). The v1 breakdown is 223 curated records + 749 backlog entries from O0000-code, 43
pinned verified records from cosen1024, 114 ranked repos from kael-odin, 281 KalarisLabs
skills, 1,129 aggregated skills, 51 ecosystem links, and 3,244 upstream `SKILL.md` files).
Each entry carries `sources[]`, licence, category, lifecycle stage, stars/trend, verification
status and an academic-relevance score.

```bash
python3 scripts/scholarforge.py registry stats
python3 scripts/scholarforge.py registry search "citation verification" --limit 10 --verified
python3 scripts/scholarforge.py registry search "latex poster" --stage figures
```
Full detail: `docs/REGISTRY.md`, `data/registry.csv`, `data/scan-summary.json`.

## When to use an external skill
ScholarForge covers the full research-and-writing lifecycle. Reach outside it only when the
task needs a **domain-specific tool** the single skill cannot embed: cryo-EM pipelines,
molecular dynamics, single-cell analysis, GPU training, chemical databases, clinical
registries, a specific publisher's Word macro, or a live database with credentials.

Selection order:
1. Does ScholarForge already do it? Use the built-in command.
2. Is the external tool in the registry with a verified record and a permissive licence?
3. Does it declare network calls, hooks, `allowed-tools` and required credentials?
4. Read its security findings (`docs/SECURITY_SCAN.md`) before installing.
5. Prefer stdlib/zero-dependency, pinned commits and offline-capable tools.

## Vetting checklist (from the ASDF framework)
- [ ] `LICENSE` present and compatible with your use (note CC BY-NC for one upstream).
- [ ] No `Bash(*)` wildcard or unrestricted shell in `allowed-tools`.
- [ ] No hooks / implicit execution you did not approve.
- [ ] No reverse shells, decode-then-exec blobs, credential-path reads, exfiltration
      endpoints, miners/RATs, unpinned auto-updating dependencies.
- [ ] Network endpoints enumerated and justified; no telemetry to undisclosed hosts.
- [ ] No prompt-injection/jailbreak markers or hidden Unicode in content files.
- [ ] Pinned commit or release; diff reviewed by a human.
- [ ] Sandbox run with no access to production credentials.

## Licensing note
The merged compilation is restricted to **non-commercial** use because
`Imbad0202/academic-research-skills` is CC BY-NC 4.0. Two upstream aggregators ship no
licence file; their snapshots are retained for attribution only, and their content is not
relicensed. See `NOTICE.md` and `upstream/LICENSES.md`.

## Data provenance
`tools/scan_sources.py`, `tools/security_scan.py`, `tools/merge_registry.py`,
`tools/package_upstream.py` are reproducible. `upstream/manifest.json` records the commit,
file count, sizes and SHA-256 for each lossless ZIP. `data/scan-inventory.json` indexes every
single file with its hash.
