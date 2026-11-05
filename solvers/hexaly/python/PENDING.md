# Pending: protocol 2 needs a re-certification with the Hexaly licence

`run.py`, `readiness_test.py`, `metadata.json` and `CONTRACT.md` are changed for protocol 2: every
solution of an optimisation carries `objective`. Certification needs the solver to run, and no
Hexaly licence is configured on this machine, so these steps are deferred. Until they are done,
this branch stays unmerged: main keeps its certified protocol 1 record.

With the licence configured (`python -m evaluation.licences set hexaly PATH`, or `DCP_LICENCE_HEXALY`):

1. `make build SOLVER=hexaly_python`
2. `make readiness SOLVER=hexaly_python FOLDER=solvers/hexaly/python`; `objective_values` must pass.
3. Re-evaluate the optimisation models of `generated_models/*/hexaly_python/` under the objective
   check, and repair any `objective_mismatch` through `generation.manage`.
4. Delete this file, and merge.
