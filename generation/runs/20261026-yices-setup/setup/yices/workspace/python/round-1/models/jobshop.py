# Job-shop scheduling: minimise the makespan by tightening an upper bound on it.
# Usage: python jobshop.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def geq_diff(x, y, d):
    # x - y >= d
    return Terms.arith_geq_atom(Terms.sub(x, y), Terms.integer(d))


def main():
    inst = json.load(open(sys.argv[1]))
    jobs = inst["jobs"]
    INT = Types.int_type()
    # the sum of all durations is a valid makespan bound (run everything in sequence)
    horizon = sum(dur for job in jobs for _, dur in job)

    ctx = Context()
    start = []
    for j, job in enumerate(jobs):
        row = []
        for k in range(len(job)):
            s = Terms.new_uninterpreted_term(INT, f"s_{j}_{k}")
            ctx.assert_formula(Terms.arith_geq_atom(s, Terms.integer(0)))
            ctx.assert_formula(Terms.arith_leq_atom(s, Terms.integer(horizon)))
            row.append(s)
        start.append(row)

    makespan = Terms.new_uninterpreted_term(INT, "makespan")
    ctx.assert_formula(Terms.arith_leq_atom(makespan, Terms.integer(horizon)))

    # precedence within a job, and every task ends by the makespan
    for j, job in enumerate(jobs):
        for k, (_, dur) in enumerate(job):
            ctx.assert_formula(geq_diff(makespan, start[j][k], dur))
            if k + 1 < len(job):
                ctx.assert_formula(geq_diff(start[j][k + 1], start[j][k], dur))

    # a machine runs one task at a time: for each pair on the same machine, one comes first
    tasks = [(start[j][k], machine, dur)
             for j, job in enumerate(jobs) for k, (machine, dur) in enumerate(job)]
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            sa, ma, da = tasks[a]
            sb, mb, db = tasks[b]
            if ma == mb:
                ctx.assert_formula(Terms.yor([geq_diff(sb, sa, da), geq_diff(sa, sb, db)]))

    best_start = None
    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        best = model.get_value(makespan)
        best_start = [[model.get_value(s) for s in row] for row in start]
        model.dispose()
        ctx.assert_formula(Terms.arith_lt_atom(makespan, Terms.integer(best)))
    ctx.dispose()
    print(json.dumps({"start": best_start}))


if __name__ == "__main__":
    main()
