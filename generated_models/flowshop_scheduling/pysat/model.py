# flowshop_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def makespan_of(order, process_time, n_machines):
    """The makespan when the jobs run in the given order, each one as early as possible."""
    end = [0] * n_machines  # end[m]: the time machine m finishes the last job placed so far
    for j in order:
        for m in range(n_machines):
            end[m] = max(end[m], end[m - 1] if m > 0 else 0) + process_time[j][m]
    return end[-1]


def create_model(instance):
    """Permutation flow shop: every job visits the machines in the same order, and every
    machine handles the jobs in one common sequence. Find the sequence of jobs that makes the
    makespan, the time when the last job leaves the last machine, as small as possible."""
    process_time = instance["process_time"]  # process_time[j][m]: time job j takes on machine m
    n_jobs = len(instance["jobs"])          # number of jobs
    n_machines = len(instance["machines"])  # number of machines
    jobs = range(n_jobs)
    machines = range(n_machines)

    # Any order of the jobs is a schedule, so the makespan of the listed order is an upper
    # bound on the best makespan.
    upper = makespan_of(list(jobs), process_time, n_machines)
    # From below, machine m cannot finish before it has done all its work, after the
    # shortest work the jobs need on the machines before it, and followed by the shortest
    # work they need on the machines after it. Nor can a job leave the last machine before
    # its own total work is done.
    lower = max(
        [sum(process_time[j][m] for j in jobs)
         + min(sum(process_time[j][:m]) for j in jobs)
         + min(sum(process_time[j][m + 1:]) for j in jobs) for m in machines]
        + [sum(process_time[j]) for j in jobs])
    lower = min(lower, upper)

    pool = IDPool()
    # pos[k][j] is true when job j is the k-th job of the sequence.
    pos = [[pool.id(("pos", k, j)) for j in jobs] for k in range(n_jobs)]
    # end[k][m] is the time the k-th job of the sequence finishes on machine m.
    end = [[Integer(f"end_{k}_{m}", 0, max(upper, 1), encoding="order", vpool=pool)
            for m in machines] for k in range(n_jobs)]
    # makespan is the time the last job leaves the last machine.
    makespan = Integer("makespan", lower, upper, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=[e for row in end for e in row] + [makespan], vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each position of the sequence holds exactly one job.
    for k in range(n_jobs):
        formula.extend(CardEnc.equals(lits=pos[k], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
    # Each job takes exactly one position of the sequence.
    for j in jobs:
        formula.extend(CardEnc.equals(lits=[pos[k][j] for k in range(n_jobs)], bound=1,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    def ge(x, v, ub):
        """The statement x >= v as a clause literal: None when it always holds, False when it never does."""
        return None if v <= 0 else (x.ge(v) if v <= ub else False)

    def at_least_after(cond, earlier, later, p):
        """When cond holds, later is at least p more than earlier (or at least p when earlier is None)."""
        ub = max(upper, 1)
        # later is at least p.
        tgt = ge(later, p, ub)
        if tgt is False:
            formula.append([-cond])
        elif tgt is not None:
            formula.append([-cond, tgt])
        if earlier is None:
            return
        # If earlier is at least v, later is at least v + p.
        for v in range(1, ub + 1):
            tgt = ge(later, v + p, ub)
            if tgt is False:
                formula.append([-cond, -earlier.ge(v)])
            elif tgt is not None:
                formula.append([-cond, -earlier.ge(v), tgt])

    # The k-th job of the sequence, say j, takes process_time[j][m] on machine m. It starts on
    # machine m only after it finishes on machine m - 1, and only after the job before it in
    # the sequence finishes on machine m. Only these lower bounds on the end times are stated:
    # a later end time than needed never lowers the makespan.
    for k in range(n_jobs):
        for m in machines:
            for j in jobs:
                p = process_time[j][m]
                at_least_after(pos[k][j], end[k][m - 1] if m > 0 else None, end[k][m], p)
                if k > 0:
                    at_least_after(pos[k][j], end[k - 1][m], end[k][m], p)

    # The makespan is at least the end time of the last job on the last machine, which is the
    # largest end time, since end times grow along the sequence and along the machines.
    last = end[n_jobs - 1][n_machines - 1]
    for v in range(lower + 1, upper + 1):
        formula.append([-last.ge(v), makespan.ge(v)])

    # Minimise the makespan: each unit above its lower bound costs 1.
    for v in range(lower + 1, upper + 1):
        formula.append([-makespan.ge(v)], weight=1)

    # The objective in the problem's terms: the makespan (RC2's cost is how far it lies above
    # the lower bound).
    return formula, {"makespan": makespan}, makespan


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
