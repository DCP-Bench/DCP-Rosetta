# flowshop_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python flowshop_scheduling.py flowshop_scheduling.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """A set of jobs is processed on a series of machines. Every job visits the machines
    in the same order, from machine 1 to machine M, and every machine handles the jobs in
    one common sequence. Find the sequence that minimises the makespan, the time when all
    jobs have been processed."""
    jobs = instance["jobs"]                  # the jobs
    schedules = instance["schedules"]        # the positions in the sequence, one for each job
    machines = instance["machines"]          # the machines, in the order every job visits them
    process_time = instance["process_time"]  # process_time[j][m]: the time job j takes on machine m
    n_jobs = len(jobs)
    n_positions = len(schedules)
    n_machines = len(machines)

    # The total processing time of all jobs on all machines; no job can finish later than this.
    horizon = sum(sum(row) for row in process_time)

    # The number of bits needed to write any time up to the horizon.
    width = max(1, horizon.bit_length())

    # x[j][p] is true when job j is at position p of the sequence
    x = [[Bool(f"x_{j}_{p}") for p in range(n_positions)] for j in range(n_jobs)]

    # The time the job at position p takes on machine m.
    def proc(p, m):
        return sum(process_time[j][m] * x[j][p] for j in range(n_jobs))

    # A time up to the horizon, written in binary: bits[k] is true when the bit of value 2**k is set.
    def completion_var(p, m):
        bits = [Bool(f"c_{p}_{m}_{k}") for k in range(width)]
        return sum((1 << k) * bits[k] for k in range(width))

    # C[p][m] is the time the job at position p leaves machine m.
    C = [[completion_var(p, m) for m in range(n_machines)] for p in range(n_positions)]

    # the rules of the schedule, one group at a time
    constraints = []

    # Each job takes exactly one position in the sequence.
    for j in range(n_jobs):
        constraints.append(sum(x[j]) == 1)

    # Each position holds exactly one job.
    for p in range(n_positions):
        constraints.append(sum(x[j][p] for j in range(n_jobs)) == 1)

    # A machine handles one job at a time: the job at position p leaves machine m only after
    # the job at position p - 1 has left it, and then takes its own time there.
    for p in range(1, n_positions):
        for m in range(n_machines):
            constraints.append(C[p][m] >= C[p - 1][m] + proc(p, m))

    # A job leaves machine m only after it has left machine m - 1, and then takes its own time on machine m.
    for p in range(n_positions):
        for m in range(1, n_machines):
            constraints.append(C[p][m] >= C[p][m - 1] + proc(p, m))

    # The first job takes its time on the first machine.
    constraints.append(C[0][0] >= proc(0, 0))

    # The time the last job leaves the last machine, to be made as small as possible.
    makespan = C[n_positions - 1][n_machines - 1]

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
