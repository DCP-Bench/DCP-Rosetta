# Nest solvers: report

All 31 integrations are nested as `solvers/<solver>/<interface>/` beside `solvers/<solver>/skills/<name>/`; each was rebuilt and re-certified (readiness check and verify), every standalone review was clean, and `check_integration.py <id>` (no --static) exits 0 for all 31 (scip_python has one warning: unpinned pip packages).

| Integration | Integration folder | Skill | Lost-content findings (count, per solver) | Review / readiness |
|---|---|---|---|---|
| choco_java | solvers/choco/java/ | solvers/choco/skills/choco/ | 0 (solver choco) | review clean; ready |
| choco_python | solvers/choco/python/ | solvers/choco/skills/choco/ | 0 (solver choco) | review clean; ready |
| chuffed_cpp | solvers/chuffed/cpp/ | solvers/chuffed/skills/chuffed/ | 1 (solver chuffed) | review clean; ready |
| clingo_asp | solvers/clingo/asp/ | solvers/clingo/skills/clingo/ | 1 (solver clingo) | review clean; ready |
| cpmpy_python | solvers/cpmpy/python/ | solvers/cpmpy/skills/cpmpy/ | 4 (solver cpmpy) | review clean; ready |
| cvc5_python | solvers/cvc5/python/ | solvers/cvc5/skills/cvc5/ | 2 (solver cvc5) | review clean; ready |
| docplex_cplex | solvers/docplex/python/ | solvers/docplex/skills/docplex/ | 0 (solver docplex) | review clean; ready |
| eclipse_clp | solvers/eclipse/prolog/ | solvers/eclipse/skills/eclipse/ | 0 (solver eclipse) | review clean; ready |
| essence_prime_minion | solvers/essence_prime/essence_prime/ | solvers/essence_prime/skills/essence-prime/ | 0 (solver essence_prime) | review clean; ready |
| exact | solvers/exact/python/ | solvers/exact/skills/exact/ | 1 (solver exact) | review clean; ready |
| gecode_cpp | solvers/gecode/cpp/ | solvers/gecode/skills/gecode/ | 0 (solver gecode) | review clean; ready |
| gurobipy_python | solvers/gurobi/python/ | solvers/gurobi/skills/gurobi/ | 3 (solver gurobi) | review clean; ready |
| hermax | solvers/hermax/python/ | solvers/hermax/skills/hermax/ | 1 (solver hermax) | review clean; ready |
| highs_cpp | solvers/highs/cpp/ | solvers/highs/skills/highs/ | 2 (solver highs) | review clean; ready |
| huub_rust | solvers/huub/rust/ | solvers/huub/skills/huub/ | 0 (solver huub) | review clean; ready |
| idp_z3 | solvers/idp_z3/idp/ | solvers/idp_z3/skills/idp-z3/ | 0 (solver idp_z3) | review clean; ready |
| jump_highs | solvers/jump/julia/ | solvers/jump/skills/jump/ | 0 (solver jump) | review clean; ready |
| maxicp_java | solvers/maxicp/java/ | solvers/maxicp/skills/maxicp/ | 0 (solver maxicp) | review clean; ready |
| minizinc_gecode | solvers/minizinc/minizinc/ | solvers/minizinc/skills/minizinc/ | 0 (solver minizinc) | review clean; ready |
| ortools_cp_sat_cpp | solvers/ortools_cp_sat/cpp/ | solvers/ortools_cp_sat/skills/ortools-cp-sat/ | 4 (solver ortools_cp_sat) | review clean; ready |
| ortools_cp_sat_python | solvers/ortools_cp_sat/python/ | solvers/ortools_cp_sat/skills/ortools-cp-sat/ | 4 (solver ortools_cp_sat) | review clean; ready |
| paramita_python | solvers/paramita/python/ | solvers/paramita/skills/paramita/ | 1 (solver paramita) | review clean; ready |
| picat | solvers/picat/picat/ | solvers/picat/skills/picat/ | 0 (solver picat) | review clean; ready |
| pulp_cbc | solvers/pulp/python/ | solvers/pulp/skills/pulp/ | 0 (solver pulp) | review clean; ready |
| pumpkin_rust | solvers/pumpkin/rust/ | solvers/pumpkin/skills/pumpkin/ | 0 (solver pumpkin) | review clean; ready |
| pycsp3_ace | solvers/pycsp3/python/ | solvers/pycsp3/skills/pycsp3/ | 0 (solver pycsp3) | review clean; ready |
| pysat | solvers/pysat/python/ | solvers/pysat/skills/pysat/ | 2 (solver pysat) | review clean; ready |
| mip_cbc | solvers/python_mip/python/ | solvers/python_mip/skills/python-mip/ | 1 (solver python_mip) | review clean; ready |
| scip_python | solvers/scip/python/ | solvers/scip/skills/scip/ | 0 (solver scip) | review clean; ready |
| swipl_clpfd | solvers/swipl/prolog/ | solvers/swipl/skills/swipl/ | 0 (solver swipl) | review clean; ready |
| z3_python | solvers/z3/python/ | solvers/z3/skills/z3/ | 2 (solver z3) | review clean; ready |

## Checks
- unittest (evaluation, generation, skill_workflow, readiness, solvers): 91 tests OK, 12 skipped.
- `generation.next_work`: all 31 integrations list skill and interface, all ready.
- Skill regression scripts in tests/ pass against the nested skills (they now read SKILL.md plus interfaces/**/*.md).

## Outside references fixed
- tests (resume regression skill path, skill-bundle regressions), generation/AGENTS.md, generation/README.md, evaluation/README.md, AGENTS.md, solvers/CONTRACT.md, solvers/SKILLS.md (tree), skills/model-generator and skills/solver-setup docs, web/minizinc.js comment, choco java README/CONTRACT links.

## Left as is
- Comments naming `solvers/cpmpy_python/readiness_test.py` in chuffed/cpp, gecode/cpp and pycsp3/python readiness_test.py: editing them changes the hash and invalidates the readiness record.
- Historical records under generation/runs and generated_models.
- tests/test_generation_containers.py builds a fake `solvers/cpmpy_python` tree; tests pass, so left.
- solvers/yices/ (c, python) has no skills folder; it was not part of this migration.
- The old flat folders' tracked files show as deleted; they still need staging.

## Blocked
Nothing.
