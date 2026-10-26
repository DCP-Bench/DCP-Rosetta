# Existing skills for Yices 2: search notes (section 2.2)

Search date: 2026-10-26. Target: Yices 2, interfaces C API and Python bindings.

## Decision

No published agent skill for Yices 2 was found in any searched source: not on the
skills.sh registry, not in the SRI-CSL repositories, not in the vendor collections
(NVIDIA, google), and no `llms.txt` / `llms-full.txt` exists on the Yices site.
Decision: write a new standalone skill `solvers/yices/skills/yices/` (no existing
same-API skill to add an interface to). Generic SMT-solver skills found on GitHub are
either multi-solver stubs or use Yices only as a backend option; none is a source
for Yices-specific API facts. Official docs and the header are the sources.

## Searches run

| Where | Command / query | Result |
|---|---|---|
| skills.sh registry | `npx skills find yices` | One hit, unrelated: `cheickdiakite-yikes/my-ai-companion@zeeme-session-continuity` (matched "yikes", not Yices). https://skills.sh/cheickdiakite-yikes/my-ai-companion/zeeme-session-continuity |
| skills.sh registry | `npx skills find yices2` | No skills found |
| skills.sh registry | `npx skills find pyyices` | No skills found |
| GitHub code search | `gh search code "yices" --filename SKILL.md` | 20+ hits, all generic (see classification) |
| GitHub code search | `gh search code "yices" --repo SRI-CSL/yices2 --filename SKILL.md` | No hits |
| GitHub code search | `gh search code "yices" --owner SRI-CSL` filtered for skill/llms | No hits |
| SRI-CSL/yices2 tree | `git/trees/master?recursive=1` filtered for skill, llms, AGENTS, CLAUDE | No hits; repo has `doc/`, `bindings/README.md`, no `skills/` or `llms.txt` at root |
| SRI-CSL/yices2_python_bindings tree | filtered for skill, llms, agents, claude | No hits |
| NVIDIA/skills tree (`git/trees/HEAD?recursive=1`) | filtered for smt, yices, solver, constraint, z3, llms | No Yices or SMT skill (only cuOpt and unrelated hits) https://github.com/NVIDIA/skills |
| google/skills tree | same filter | No Yices or SMT skill https://github.com/google/skills |
| Yices web site | `https://yices.csl.sri.com/llms.txt` | HTTP 404 (Apache) |
| Web search | "Yices 2 SMT solver agent skill SKILL.md llms.txt" | No Yices skill; only a Z3 skill commit (other solver) |

Not run: `uvx library-skills` (the Yices Python wheel is not installed on the host, and
installing it is not allowed). The PyPI package `yices` is listed as a source below
for the companion check, so a later check inside the image is still possible.

## Classification of GitHub code-search hits

| Found skill | Role | Why |
|---|---|---|
| a5c-ai/babysitter, `library/specializations/domains/science/computer-science/skills/smt-solver-interface/SKILL.md` (https://github.com/a5c-ai/babysitter/blob/main/library/specializations/domains/science/computer-science/skills/smt-solver-interface/SKILL.md) | Ignore | Generic "Interface with SMT solvers" skill across solvers; the body is a thin, solver-agnostic template and gives no Yices API facts. It would compete on triggers with a Yices skill. |
| K-Dense-AI/scientific-agents, `formal-methods-researcher/SKILL.md` and its mirrors (stanfish06, raktim-mondol, Tashima-Tarsh, Mr-Nobody-Anonymous) (https://github.com/K-Dense-AI/scientific-agents) | Ignore | Mentions Yices only in one line (a list of solvers, `--produce-models`, unsat cores, push/pop); a formal-methods research skill, not Yices modelling. Identical copies across mirrors. |
| Halmos skill, hairyf/blockchain-skills `skills/halmos/SKILL.md` (https://github.com/hairyf/blockchain-skills) | Ignore | Halmos is a symbolic tester for EVM contracts; Yices is one of its `--solver` options. Irrelevant to Yices modelling. |
| yosys/sby skills (EDAPack/yosys-bin `skills/sby/SKILL.md`; vibeic/vibe-ic formal-verify; rtl-buddy; babyworm rtl-p5s-sva-policy; Gateflow gf-formal) | Ignore | Hardware formal verification drivers; Yices appears as a `smtbmc` engine or a table row. Not about the Yices API. |
| sufield/stave writing-reasoning-specs; vibey theory-of-computation; qhjqhj00 qnn-smt-verification-eval; hiyenwong llm2cert; lach-matt science-tools; claudebreak2 | Ignore | Mention Yices in a list of solvers or a table row; not Yices skills. |
| Z3 commit adding `.github/skills/` (git.libre-chip.org mirror of Z3) | Ignore | Z3 skills, a different solver. Cited only as a precedent for the SKILL.md + scripts layout. |

No hit qualifies as **source** or **companion**. Nothing is recommended for installation.

## Facts with sources

| Fact | Source |
|---|---|
| Yices 2 is an SMT solver; accepts SMT-LIB 2.0 and 1.2 input and Yices' own specification language | https://github.com/SRI-CSL/yices2/blob/master/README.md ; https://yices.csl.sri.com/ |
| Official C API is `src/include/yices.h` | https://github.com/SRI-CSL/yices2/blob/master/README.md (links `src/include/yices.h`) |
| Official bindings: Python, Java, Go, OCaml, each in its own repo | https://github.com/SRI-CSL/yices2/blob/master/bindings/README.md |
| Python bindings repo: `SRI-CSL/yices2_python_bindings`, MIT licence, last push 2024-12-18 | `gh api repos/SRI-CSL/yices2_python_bindings` ; https://github.com/SRI-CSL/yices2_python_bindings |
| Python bindings: PyPI `yices`, latest version 1.1.6, summary "Python Bindings for the Yices SMT Solver", PyPI metadata licence GPLv3 | https://pypi.org/project/yices/ (JSON: https://pypi.org/pypi/yices/json) |
| Python bindings README: install Yices first, then `pip install yices`; installs packages `yices_api` (ctypes wrapper of yices.h), `yices` (Pythonic API), and `yices_python_info` | https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/README.md |
| Yices 2 core licence GPL-3.0; alternative licence terms via fm-licensing@csl.sri.com | https://github.com/SRI-CSL/yices2 (GitHub licence field) ; https://yices.csl.sri.com/ |
| Latest release tag `yices-2.7.0`, published 2025-07-16 | https://api.github.com/repos/SRI-CSL/yices2/releases/latest ; https://yices.csl.sri.com/ ("Yices 2.7.0, released on 2025-07-16") |
| Repo last pushed 2026-10-22 | `gh api repos/SRI-CSL/yices2` |
| Docs on site: manual PDF (`papers/manual.pdf`), API reference (`doc/index.html`), general docs page | https://yices.csl.sri.com/ ; HTTP 200 for https://yices.csl.sri.com/doc/index.html and https://yices.csl.sri.com/papers/manual.pdf |
| Repo docs include `doc/manual/manual.tex`, `doc/sphinx/source/`, `doc/YICES-LANGUAGE`, `doc/SMT-LIB-LANGUAGE` | https://github.com/SRI-CSL/yices2/tree/master/doc |
| Site has no mention of llms.txt or agent skills; `llms.txt` returns 404 | https://yices.csl.sri.com/ ; https://yices.csl.sri.com/llms.txt |
| Yices install options on the site: Homebrew, apt/PPA, precompiled 64-bit Linux and macOS binaries | https://yices.csl.sri.com/ |

## Notes for the skill author

- Docs site and repo `doc/` are the official sources for the standalone skill. Those
  claims must be run before they go into the skill (section 2.3 of the procedure).
- The repo README says the C API and Python bindings exist; the notes do not confirm
  which Python package the PyPI name `yices` installs versus the older `yices` bindings
  repo. Check in the image before writing `interfaces/python.md`.
- Python bindings licence is listed as MIT on the GitHub repo and as GPLv3 in PyPI
  metadata. Record both in `sources.md` and resolve during setup.
- Last Python bindings push was 2024-12-18; the core repo was pushed 2026-10-22.
