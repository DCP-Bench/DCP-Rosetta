"""Job-shop scheduling with Yices, minimising the makespan.

Each task has an integer start time. Tasks of one job run in order, and tasks
on one machine do not overlap. The makespan variable M bounds every task end;
M is tightened after each model until the solver proves optimality.
"""
import json
import sys
from pathlib import Path

from yices import Context, Model, Status, Terms, Types

inst = json.loads(Path(sys.argv[1]).read_text())
jobs = inst["jobs"]
machine = [[m for m, _ in job] for job in jobs]
dur = [[d for _, d in job] for job in jobs]
horizon = sum(sum(row) for row in dur)

INT = Types.int_type()
zero = Terms.integer(0)
start = [[Terms.new_uninterpreted_term(INT, f"s_{j}_{k}") for k in range(len(job))]
         for j, job in enumerate(jobs)]
makespan = Terms.new_uninterpreted_term(INT, "makespan")


def end(j, k):
    """The end time of task k of job j as a term."""
    return Terms.add(start[j][k], Terms.integer(dur[j][k]))


ctx = Context()

# Start times are non-negative; the makespan is at most the total work.
for j, job in enumerate(jobs):
    for k in range(len(job)):
        ctx.assert_formula(Terms.arith_geq_atom(start[j][k], zero))
        ctx.assert_formula(Terms.arith_leq_atom(end(j, k), makespan))
ctx.assert_formula(Terms.arith_geq_atom(makespan, zero))
ctx.assert_formula(Terms.arith_leq_atom(makespan, Terms.integer(horizon)))

# A task starts after the previous task of its job has finished.
for j, job in enumerate(jobs):
    for k in range(len(job) - 1):
        ctx.assert_formula(Terms.arith_leq_atom(end(j, k), start[j][k + 1]))

# Tasks on the same machine do not overlap.
tasks = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
for a in range(len(tasks)):
    for b in range(a + 1, len(tasks)):
        ja, ka = tasks[a]
        jb, kb = tasks[b]
        if machine[ja][ka] != machine[jb][kb]:
            continue
        ctx.assert_formula(Terms.yor([
            Terms.arith_leq_atom(end(ja, ka), start[jb][kb]),
            Terms.arith_leq_atom(end(jb, kb), start[ja][ka]),
        ]))

best = None
best_start = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    starts = [[model.get_value(s) for s in row] for row in start]
    model.dispose()
    best_start = starts
    best = max(starts[j][k] + dur[j][k]
               for j, job in enumerate(jobs) for k in range(len(job)))
    # Ask for a schedule that finishes strictly earlier.
    ctx.assert_formula(Terms.arith_leq_atom(makespan, Terms.integer(best - 1)))
ctx.dispose()

if best_start is None:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    print(json.dumps({"start": best_start}))
