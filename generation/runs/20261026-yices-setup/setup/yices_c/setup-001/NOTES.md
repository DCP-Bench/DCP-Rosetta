yices_c integration: files solvers/yices/c/{Dockerfile,metadata.json,run.py,c/dcp.h,c/driver.c,CONTRACT.md,readiness_test.py,readiness*.json}, tests/fixtures/model_yices_c.c.
Design: harness parses (cJSON), submission defines build(const cJSON*); driver.c owns main/contexts; linear tightening, fresh pinned context for enumeration, value no-goods, SIGALRM+yices_stop_search.
Evidence: build.log, readiness-run1.json (30 checks true), readiness-check.txt, readiness-verify.txt, check_static.txt, check_full.txt (only registration failures), probe_big_nia.*, smoke.sh.
