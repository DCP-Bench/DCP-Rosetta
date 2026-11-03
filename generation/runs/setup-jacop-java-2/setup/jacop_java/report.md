# jacop_java setup, run setup-jacop-java-2

Result: ready (readiness_level 2). Docker builds used DOCKER_BUILDKIT=0 (buildkit cache dir missing on this host).

Changed: Dockerfile unchanged (base pinned by digest, jars by sha256, python3 by version); Model.java (putDigits, Long values),
Runner.java (FailException note in error detail), readiness_test.py (level-2 checks, out_of_memory), metadata.json (readiness_level 2),
CONTRACT.md (new), tests/fixtures/model_jacop_java.java, PILOTS and MAXIMIZATION_SWAPS in tests/test_solvers.py, README.md name.
Stale "compilation": true kept: the schema accepts it.

Versions: JaCoP 4.10.0, org.json 20250517, Temurin 21.0.8_9. Image id 4d219ef6d616... (dcp-eval/jacop_java:v1).
Skill checks: generation.skills validate OK, rosetta-mentions OK, check_assets --image 3/3 pass, standalone-review.json verdict standalone (fresh subagent).
Commands: check_integration.py jacop_java (45 passed, 0 failed), generation.readiness check (all checks passed), pytest tests/test_solvers.py (8 passed, 12 skipped).
Capabilities: global constraints (Alldiff, Cumulative, Circuit, Element, Table, Regular, Count, Diff2, ...), optimisation with proven optimum, enumeration of distinct outputs. Limits: 32-bit IntVar, no search of its own in submission, no float/set vars used.
