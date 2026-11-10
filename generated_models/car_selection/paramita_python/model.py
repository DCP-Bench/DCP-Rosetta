# car_selection: a Paramita (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python car_selection.py car_selection.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Assign participants to cars to maximise the number of assignments: each participant is
    interested in a subset of the cars, gets at most one car, and each car goes to at most one
    participant."""
    interest = instance["possible_assignments"]  # interest[i][j] is 1 when participant i wants car j
    n_participants = len(interest)
    n_cars = len(interest[0])

    # assignments[i][j] is true when participant i is assigned to car j
    assignments = [[Bool(f"a_{i}_{j}") for j in range(n_cars)] for i in range(n_participants)]

    constraints = []  # the rules of the assignment

    # A participant is assigned only a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            if interest[i][j] == 0:
                constraints.append(~assignments[i][j])

    # Each participant is assigned at most one car.
    for i in range(n_participants):
        constraints.append(sum(assignments[i]) <= 1)

    # Each car is assigned to at most one participant.
    for j in range(n_cars):
        constraints.append(sum(assignments[i][j] for i in range(n_participants)) <= 1)

    # The number of assignments is to be maximised.
    total = sum(assignments[i][j] for i in range(n_participants) for j in range(n_cars))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(total, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of assignments, maximised (the
    # soft clauses maximise it).
    return (formula, pool), {"assignments": assignments}, total


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
