Blind model, after reading the lessons of 20261016-maxicp-java-models (cumulative, implied bounds
and pairwise noOverlap did not prove json:2 and json:3). Measured locally:
- intervals + precedences + cumulative per resource (either algorithm): json:2 and json:3 time out;
- plus a noOverlap over each greedy clique of jobs that pairwise cannot overlap (needs summing
  above a capacity): json:2 in 9-38 s, json:3 in about 295 s;
- plus a registered order Boolean per such pair, so firstFailBinary posts precedences before it
  sets start times: every instance in under 5 s. That is this attempt (BELDICEANU_CARLSSON
  cumulative). The horizon is the sum of durations.
