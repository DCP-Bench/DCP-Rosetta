# Resume notes, run hexaly-rest-20261102t225510z-cea0

The run was paused by the user while evaluating; nothing was running, and no container was left behind.

State at the pause:

- 76 problems were queued for `hexaly_python` (the rest of the `next_work` queue after the earlier batches).
- A model is written for every one of them (`attempts/<problem>/hexaly_python/attempt-001/model.py`).
- 17 are evaluated, accepted and retained: session1_magic_square, session1_money_change,
  session2_maximal_independent_sets, session2_movie_scheduling, session2_subset_sum, session2_subsets_100,
  session3_farmer_and_cows, session3_kidney_exchange, session5_climbing_stairs, session5_grocery (4 of 5, the
  example instance unproven), set_game, sudoku, three_sum, tsp, twelve_pack, wolf_goat_cabbage, csplib_044_steiner.
- csplib_003_quasigroup_existence attempt-001 was evaluated and not retained (2 of 4 instances; the order 8 and
  order 9 instances ended without a proven result). Its repair is attempt-002, written, not evaluated.
- session5_grocery attempt-002 (prices restricted to divisors of the product) is written, not evaluated; retain it
  only if it is accepted on all 5 instances.
- csplib_002_template_design attempt-001 was being evaluated when the run stopped; it has a preserved
  candidate.json/candidate.py and no evaluation.json, so `generation.manage evaluate` runs it again unchanged.
- The other attempts have no evaluation record yet (list them with: attempts with no evaluation.json).

How to continue (one evaluation at a time: the Hexaly licence allows a single concurrent use):

    python -m generation.manage evaluate --attempt generation/runs/hexaly-rest-20261102t225510z-cea0/attempts/<problem>/hexaly_python/attempt-001         --model generation/runs/hexaly-rest-20261102t225510z-cea0/attempts/<problem>/hexaly_python/attempt-001/model.py
    python -m generation.manage retain --attempt <the same attempt path>      # only when accepted

The image `dcp-eval/hexaly_python:v1` must exist on the machine (it holds the licence; rebuild with
`DCP_SECRET_HEXALY_LICENSE=<path to license.dat> python -m evaluation.build hexaly_python` if it is gone).
`evidence/queue-chunk1a.txt` and `evidence/queue-chunk1b.txt` are the evaluation summaries printed so far.
