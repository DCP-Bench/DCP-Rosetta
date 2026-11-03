# resource_constrained_project_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Start each job of a project so that every job starts after its predecessors have
    finished and no resource is used beyond its capacity at any time, with the project
    finishing as early as possible."""
    durations = instance["durations_data"]              # durations[j]: how long job j takes
    needs = instance["resource_needs_data"]             # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]   # capacities[r]: units of resource r available at any time
    precedences = instance["successors_link_data"]      # [a, b]: job a comes before job b
    n_jobs = len(durations)                             # the number of jobs
    n_resources = len(capacities)                       # the number of resources
    horizon = sum(durations)                            # running all jobs one after another always fits in this time
    sink = n_jobs - 1                                   # the last job is a dummy of duration 0 that follows all others

    # start_at_or_after[j][t] is true when job j starts at time t or later
    start_at_or_after = [[Bool(f"start_{j}_ge_{t}") for t in range(horizon + 2)] for j in range(n_jobs)]

    constraints = []

    # Start times run from 0 to the horizon.
    for j in range(n_jobs):
        constraints.append(start_at_or_after[j][0])
        constraints.append(~start_at_or_after[j][horizon + 1])
        constraints += [If(start_at_or_after[j][t + 1], start_at_or_after[j][t]) for t in range(horizon + 1)]

    # Job b starts only after job a has finished: at least durations[a] after job a starts.
    for pred, succ in precedences:
        for t in range(horizon + 1):
            constraints.append(If(start_at_or_after[pred][t],
                                  start_at_or_after[succ][min(t + durations[pred], horizon + 1)]))

    # running[(j, t)] is true when job j is in progress at time t, that is, it starts in the
    # last durations[j] time units up to and including t. Jobs of duration 0 and jobs that use
    # no resource are left out, since they never take any capacity.
    running = {}
    for j in range(n_jobs):
        d = durations[j]
        if d == 0 or all(need == 0 for need in needs[j]):
            continue
        for t in range(horizon):
            earliest = max(0, t - d + 1)
            running[(j, t)] = Bool(f"run_{j}_{t}")
            constraints.append(Iff(running[(j, t)],
                                   start_at_or_after[j][earliest] & ~start_at_or_after[j][t + 1]))

    # At every time, the jobs in progress use no more units of each resource than its capacity.
    for t in range(horizon):
        for r in range(n_resources):
            # usage: units of resource r used by the jobs in progress at time t
            usage = [needs[j][r] * running[(j, t)] for j in range(n_jobs) if (j, t) in running and needs[j][r] > 0]
            if usage:
                constraints.append(sum(usage) <= capacities[r])

    # start_time[j] is the start of job j: the number of times t from 1 to the horizon at which
    # job j has started.
    start_time = [sum(start_at_or_after[j][t] for t in range(1, horizon + 1)) for j in range(n_jobs)]

    # The project ends when the dummy last job starts.
    makespan = start_time[sink]

    # Finish the project as early as possible.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-makespan, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"start_time": start_time}


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
