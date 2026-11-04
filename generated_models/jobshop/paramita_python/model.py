# jobshop: a Paramita (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python jobshop.py jobshop.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def _int(name, ub):
    # A whole number from 0 to ub. bits[k] is worth 2**k.
    nb = max(1, ub.bit_length())
    bits = [Bool(f"{name}_b{k}") for k in range(nb)]
    value = sum((2 ** k) * b for k, b in enumerate(bits))
    return value, [value <= ub]


def create_model(instance):
    """Schedule the tasks of several jobs on machines so that the tasks of each job run in
    their given order, a machine works on one task at a time, and a task runs to
    completion once started. Minimize the makespan, the time the last job finishes."""
    jobs = instance["jobs_data"]  # jobs[j][k] is [machine, duration] of task k of job j

    # Running all tasks one after another takes the sum of all durations, so no task
    # needs to end after this.
    horizon = sum(duration for job in jobs for _, duration in job)

    constraints = []  # the constraints of the model
    # start[j, k] is the time task k of job j starts
    start = {}
    for j, job in enumerate(jobs):
        for k in range(len(job)):
            start[j, k], within_horizon = _int(f"start_{j}_{k}", horizon)
            constraints += within_horizon

    # A task cannot start before the previous task of its job has ended.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            constraints.append(start[j, k] + job[k][1] <= start[j, k + 1])

    # by_machine[m] lists the (job, task) pairs that run on machine m.
    by_machine = {}
    for j, job in enumerate(jobs):
        for k, (machine, _) in enumerate(job):
            by_machine.setdefault(machine, []).append((j, k))

    # Two tasks on the same machine do not overlap: one ends before the other starts.
    # first is true when the first task of the pair goes first.
    for machine, pairs in sorted(by_machine.items()):
        for a in range(len(pairs)):
            for b in range(a + 1, len(pairs)):
                j1, k1 = pairs[a]
                j2, k2 = pairs[b]
                d1 = jobs[j1][k1][1]
                d2 = jobs[j2][k2][1]
                first = Bool(f"first_m{machine}_{j1}_{k1}_{j2}_{k2}")
                constraints.append(If(first, start[j1, k1] + d1 <= start[j2, k2]))
                constraints.append(If(~first, start[j2, k2] + d2 <= start[j1, k1]))

    # The makespan is the time the last task of each job ends.
    makespan, within_horizon = _int("makespan", horizon)
    constraints += within_horizon
    for j, job in enumerate(jobs):
        if job:
            k = len(job) - 1
            constraints.append(start[j, k] + job[k][1] <= makespan)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-makespan, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
