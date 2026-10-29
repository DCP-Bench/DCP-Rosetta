# Open pairs campaign notes

Run `20261029-generate-open-pairs`: the 15 pairs `generation.next_work` still listed on 29 October
(choco_java, idp_z3, maxicp_java, mip_cbc). Profile: 99 instances, 2 solutions, 180 s, 2048 MB, one CPU,
`tolerate_inconclusive`. 13 models were accepted and retained; mip_cbc on Golomb rulers and on perfect
square placement were blocked (`generation/blockers.json`). Each attempt's `lessons.md` records what was
tried and measured.

## Models to review

Judgement calls a reviewer should check; each holds for the current instances, but not necessarily beyond.

- **de_bruijn_sequence / idp_z3** (attempt-001). IDP-Z3 cannot compute `base^n` for the sequence length, so
  the model counts over six symbol slots. It is exact only up to order n = 6 and refuses larger orders. All
  current instances have n <= 5; an instance with n > 6 would be refused, not answered wrongly.
- **big_bang2 / maxicp_java** (attempt-001). Each die's faces are constrained to increasing order. A die is
  a set of faces, so no set of dice is lost, but the order of the faces in the output is fixed by this choice
  rather than by the problem.
- **csplib_001_car_sequencing / maxicp_java** (attempt-001). The MaxiCP runner fixes the search
  (firstFailBinary, smallest value first), so the model steers it by the order it registers variables in.
  The order of car types (option load over the square root of demand) was found by trying alternatives on
  the instances, not derived; the model says so in a comment. It may not carry over to new instances.
- **csplib_002_template_design / maxicp_java** (attempt-001). Booleans make the search try the lowest sheet
  count first (a lower bound derived from the data), then one more, and so on. Every objective value stays
  allowed, so optimality is unaffected.
- **csplib_032_max_density_still_life / maxicp_java** (attempt-001). Adds the implied constraint "any 3x3
  square of a still life holds at most 6 live cells", checked exhaustively with a script before use.
- **csplib_076_costas_arrays / mip_cbc** (attempt-001). Accepted on 4 of 5 instances: on n = 12 CBC found
  one array but not a second within 180 s (the one skip the policy allows).

The other maxicp_java models use the same technique as car sequencing, within the rules: which variables are
registered and in what order, Booleans that negate registered ones so the "yes" branch is tried first, and
constraints the problem implies.

## Blocked

- **csplib_006_golomb_rulers / mip_cbc**: sizes 9 and 10 time out. On size 9 CBC's bound reaches 43 against
  the optimum 44 but it finds no ruler; given the greedy ruler as a start, it never improves on it.
- **csplib_009_perfect_square_placement / mip_cbc**: the exact-cover model (a 0/1 variable per square and
  position) exceeds 2048 MB on json:5 and json:6, even with CBC's preprocessing and heuristics off; a big-M
  non-overlap formulation with strip sums found no solution in 170 s. Attempt-002 sets CBC parameters through
  `mip.cbc.cbc_set_parameter`; it is kept only as evidence.

## Housekeeping

The run folder still holds the `candidate.*` and `readiness.json` files. `generation/AGENTS.md` asks for a
finished run to be trimmed to the ledger and the verdicts; no helper does that, and earlier runs were not
trimmed either.
