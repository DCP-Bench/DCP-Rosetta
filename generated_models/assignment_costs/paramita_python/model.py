# assignment_costs: a Paramita (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python assignment_costs.py assignment_costs.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Assign people to tasks with different costs so that the total cost is as low as
    possible. Each task goes to exactly one person, but not every person needs a task."""
    cost = instance["cost"]  # cost[i][j] is the cost of person j doing task i
    n_tasks = len(cost)      # the number of tasks
    n_people = len(cost[0])  # the number of people

    # assigned[i][j] is true when task i is done by person j
    assigned = [[Bool(f"x_{i}_{j}") for j in range(n_people)] for i in range(n_tasks)]

    constraints = []  # the rules the assignment must satisfy
    # Each task is done by exactly one person.
    for i in range(n_tasks):
        constraints.append(sum(assigned[i]) == 1)
    # Each person does at most one task.
    for j in range(n_people):
        constraints.append(sum(assigned[i][j] for i in range(n_tasks)) <= 1)

    # The total cost of the chosen assignments.
    total_cost = sum(cost[i][j] * assigned[i][j] for i in range(n_tasks) for j in range(n_people))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"x": assigned}


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
