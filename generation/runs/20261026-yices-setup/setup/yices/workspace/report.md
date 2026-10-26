# Yices 2 setup report (run 20261026-yices-setup)

## Skill
- Path: `solvers/yices/skills/yices/` (SKILL.md, interfaces/c.md, interfaces/python.md, assets/c, assets/python, sources.md, evals/evals.json).
- Decision: new skill `yices` with two interfaces, `c` and `python`. No existing skill of the same API existed to extend.
- Tested versions: Yices 2.7.0 built from source with MCSAT (libpoly v0.2.1, CUDD 3.0.0), Python bindings `yices` 1.1.6 on Python 3.12.11, Debian bookworm amd64, gcc 12.2.0, cJSON 1.7.15 (C). Skill stays unpinned.
- Images: dcp-eval/yices_c:v1 (sha256:8c967c527652b8ec72e3866b5c0625e2ba7a11b865b62590234fef8e39260e41), dcp-eval/yices_python:v1 (sha256:e38150bc3d672fc88f20f9ef2653794c0927ed1363c2ef6cd3bcf3aaaf60dfb0).

## Existing skills
None found (skills.sh, SRI-CSL repos, NVIDIA and google collections, llms.txt absent). Generic multi-solver SMT skills: ignored (stubs, Yices only as a backend option). No source and no companion; see research/existing-skills.md.

## Toy tests (18 instances per round, fresh agent per round)
| Interface | Round | Result |
|---|---|---|
| c | round-1 | 18/18 passed |
| c | round-2 | 18/18 passed |
| c | round-3 | 18/18 passed |
| c | round-final | 18/18 passed |
| python | round-1 | 18/18 passed |
| python | round-final | 18/18 passed |

The final rounds are the shipped skill; every earlier round also passed 18/18 (rounds were reruns after skill or contract edits). Results: `*/round-*/results.txt`.

## Review council
Standalone review: last pass clean, verdict standalone, no findings. Saved as `solvers/yices/standalone-review.json`. Contract fixes after the review touched only the two CONTRACT.md files, not the skill.

## Readiness
- yices_c: level 2, all checks passed (including crash-with-signal, builder error, QF_NIA); readiness.json recorded, check and verify passed; check_integration.py yices_c without --static: 47 passed, 0 failed.
- yices_python: level 2, all checks passed; check_integration.py yices_python without --static: 46 passed, 0 failed.
- Registered in tests/test_solvers.py (PILOTS, MAXIMIZATION_SWAPS), generate_site.py (LANGUAGES c, EXTENSION_LANGUAGE .c, BACKEND_NAMES yices) and README.md. Unit tests: 91 OK, 12 skipped (not investigated).
- CONTRACT.md files were corrected after readiness by reading run.py/driver.c; check_integration was not rerun after that edit (no .venv), and readiness.json does not cover CONTRACT.md.

## Known gaps
- Not run: Python install block with prefix /usr/local and sudo (images use another prefix plus ldconfig).
- The 12 skipped unit tests were not examined.
- Licence: Yices core GPL-3.0; binding licence MIT in repo vs GPLv3 on PyPI, not re-checked inside the wheel.
- C submissions must not call exit/abort; Python int output leaves are term handles (use Terms.integer).
- Leftover files: readiness-report.json/readiness-result.json kept per repo convention; readiness-stderr.log is git-ignored.
