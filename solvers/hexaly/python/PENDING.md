# Hexaly (Python): deferred steps, pending the licence

Status: licence_pending. Done without a licence: the image is rebuilt without any
licence in it, `check_integration.py hexaly_python --static` passes (44/44), the
`licence_missing` check passes, and `make test` passes. The old readiness record is
superseded (`readiness/superseded/readiness.json`), so `hexaly_python` has no current
record until the steps below run.

Licence to-do first: get a Hexaly `license.dat` as described in `solvers/hexaly/LICENCE.md`.

Run these in order, from the repository root.

1. Configure and verify the licence (the file is never read by these commands):

   ```sh
   python -m evaluation.licences set hexaly ~/.config/dcp-rosetta/licences/hexaly/license.dat
   python -m evaluation.licences check hexaly        # must print PASS and exit 0
   ```

2. Run the standalone skill's examples in the image, with the licence bound as the
   evaluator binds it:

   ```sh
   python skills/solver-setup/scripts/check_assets.py solvers/hexaly/skills/dcp-hexaly \
       --interface python --image dcp-eval/hexaly_python:v1 \
       --mount ~/.config/dcp-rosetta/licences/hexaly/license.dat:/run/licence/license.dat:ro \
       --env HX_LICENSE_PATH=/run/licence/license.dat
   ```

   Then re-run the skill's hello-world and tiny models of each kind (solver-setup 2.3) in
   the same container, and clear the `unverified: needs a licence` markers in
   `solvers/hexaly/skills/dcp-hexaly/sources.md` if any were added. The skill text
   itself is unchanged, so the toy-problem rounds (solver-setup 2.5) are not needed
   unless the skill is edited.

3. Recertify the readiness record (write-once; `readiness/superseded/` keeps the old one):

   ```sh
   python -m generation.readiness check --solver hexaly_python \
       --output solvers/hexaly/python/readiness.json
   python -m generation.readiness verify --solver hexaly_python \
       --record solvers/hexaly/python/readiness.json
   ```

   The check must pass every required and level-2 check, including `licence_missing`.

4. Confirm the integration end to end (must exit 0 before it counts as ready):

   ```sh
   python skills/solver-setup/scripts/check_integration.py hexaly_python
   ```

5. Run the pilot tests against the image, with the licence configured on this machine:

   ```sh
   DCP_CONTAINER_TESTS=1 python -m unittest tests.test_solvers
   ```

   The Hexaly pilot runs (and is skipped, with the reason, without the licence).

6. Delete this file once steps 1 to 5 pass.

Then the models: re-run the kept Hexaly models under `generated_models/` against the
licensed integration (the evaluator decides what stays). Model generation is a separate
campaign and is not part of these steps.
