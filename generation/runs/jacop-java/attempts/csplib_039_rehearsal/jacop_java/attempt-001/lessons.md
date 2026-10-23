# csplib_039_rehearsal, jacop_java: lessons

- The wait for a player is the time from the start of their first piece to the end of
  their last piece, minus the time they play. The model writes the time with prefix
  sums of slot durations (`start[]`), indexed by the variable first and last slot
  through `Element`.
- Which pieces a player plays is fixed by the instance, so each player's first and
  last slot are `Min` and `Max` over a static list of position variables, with no
  conditional. Players who play nothing contribute nothing and are skipped.
- Accepted on all 5 instances on the first evaluation.
