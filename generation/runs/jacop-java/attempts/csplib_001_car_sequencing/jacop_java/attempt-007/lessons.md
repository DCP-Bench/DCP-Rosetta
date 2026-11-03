# Lessons: csplib_001_car_sequencing, jacop_java

- The example (10 cars) is accepted by every version tried. json:1 (200 cars, 24 types, 5 options) finds no first solution in 180 s for any encoding tried.
- Encodings tried: Element-based option variables with GCC counts (attempt-001, attempt-003); the same with the runner's default search order (attempt-001 default, attempt-004 left-to-right slot order); smallest-domain slot order (attempt-005); channelled Boolean at[p][c] with reified XeqC (attempt-006); demand-ranked value order on top of that (attempt-007).
- The runner's default search (smallest domain over all variables) picks the 0/1 option variables before the slots. Passing the slot array to Model.search avoids that, but it did not make json:1 solvable.
- Official evaluation (profile instance_count 99, tolerate_inconclusive) was still running at the checkpoint, after 25 minutes. Its evaluation.json will appear in this directory when it finishes. Nothing is retained.
