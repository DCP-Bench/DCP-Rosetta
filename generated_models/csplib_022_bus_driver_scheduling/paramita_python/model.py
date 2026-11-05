# csplib_022_bus_driver_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Choose shifts so that every piece of work is covered by exactly one chosen shift,
    using as few shifts as possible. Each shift covers some of the pieces of work."""
    num_work = instance["num_work"]    # the number of pieces of work to cover
    num_shifts = instance["num_shifts"]  # the number of possible shifts
    shifts = instance["shifts"]        # shifts[s]: the pieces of work that shift s covers

    # selected[s] is true when shift s is chosen
    selected = [Bool(f"selected_{s}") for s in range(num_shifts)]

    # covering[w]: the shifts that cover piece of work w
    covering = [[] for _ in range(num_work)]
    for s, tasks in enumerate(shifts):
        for w in tasks:
            covering[w].append(selected[s])

    constraints = []

    # Each piece of work is covered by exactly one chosen shift.
    for w in range(num_work):
        constraints.append(sum(covering[w]) == 1)

    # n_selected: the number of chosen shifts. Every shift costs the same, so the fewest
    # shifts is the cheapest schedule.
    n_selected = sum(selected)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-n_selected, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of shifts selected, minimised
    # (its negation is what the soft clauses maximise).
    return (formula, pool), {"x": selected}, n_selected


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

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
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
