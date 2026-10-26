# Job shop: 3 jobs, each runs its tasks in order on given machines; no two tasks overlap on a machine.
# Minimise the makespan under a time limit.
import time
from yices import Context, Model, Status, Terms, Types

# jobs[j] = [(machine, duration), ...] in order
jobs = [[(1, 2), (0, 3), (2, 1)], [(0, 3), (2, 2), (1, 2)], [(2, 1), (1, 4)]]
num = Terms.integer
horizon = sum(d for job in jobs for _, d in job)       # a safe upper bound on any start time
start = [[Terms.new_uninterpreted_term(Types.int_type(), f"s{j}_{k}") for k in range(len(job))]
         for j, job in enumerate(jobs)]
makespan = Terms.new_uninterpreted_term(Types.int_type(), "makespan")

ctx = Context()
for j, job in enumerate(jobs):
    for k, (_, d) in enumerate(job):
        s = start[j][k]
        ctx.assert_formula(Terms.arith_geq_atom(s, num(0)))                       # start at time 0 or later
        ctx.assert_formula(Terms.arith_leq_atom(Terms.add(s, num(d)), makespan))  # ends before the makespan
        if k + 1 < len(job):                                                      # tasks of a job in order
            ctx.assert_formula(Terms.arith_leq_atom(Terms.add(s, num(d)), start[j][k + 1]))
ctx.assert_formula(Terms.arith_leq_atom(makespan, num(horizon)))
# no overlap on a machine: one of two tasks finishes before the other starts
tasks = [(j, k, m, d) for j, job in enumerate(jobs) for k, (m, d) in enumerate(job)]
for a in range(len(tasks)):
    for b in range(a + 1, len(tasks)):
        (j1, k1, m1, d1), (j2, k2, m2, d2) = tasks[a], tasks[b]
        if m1 == m2 and j1 != j2:
            ctx.assert_formula(Terms.yor([
                Terms.arith_leq_atom(Terms.add(start[j1][k1], num(d1)), start[j2][k2]),
                Terms.arith_leq_atom(Terms.add(start[j2][k2], num(d2)), start[j1][k1])]))

deadline = time.time() + 20.0
best, plan, proven = None, None, False
while True:
    left = deadline - time.time()
    if left <= 0:
        break
    status = ctx.check_context(timeout=left)       # seconds; INTERRUPTED when the limit is hit
    if status == Status.SAT:
        model = Model.from_context(ctx, 1)
        best = model.get_value(makespan)
        plan = [[model.get_value(s) for s in row] for row in start]
        model.dispose()
        ctx.assert_formula(Terms.arith_lt_atom(makespan, num(best)))
    else:
        proven = status == Status.UNSAT            # UNSAT after a SAT: best is optimal
        break
if best is None:
    print("No solution found", "(infeasible)" if proven else "(limit reached)")
else:
    print("Makespan:", best, "(optimal)" if proven else "(best found, not proven)")
    print("Starts:", plan)
