# room_assignment: a Paramita (Python) model from DCP Rosetta.
# Download the `room_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/room_assignment.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python room_assignment.py room_assignment.json

from datetime import date

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Assign each request, a stay from a start date to an end date, to one room for its
    whole stay, so that a room never serves two requests at once. Some requests already
    have a room."""
    max_rooms = instance["max_rooms"]                                  # the number of rooms, numbered 0 .. max_rooms - 1
    starts = [date.fromisoformat(s) for s in instance["start_data"]]   # starts[i]: first day of the stay of request i
    ends = [date.fromisoformat(e) for e in instance["end_data"]]       # ends[i]: day request i checks out
    preassigned = instance["preassigned_room_data"]                    # preassigned[i]: room fixed for request i, -1 if none
    n_requests = len(starts)                                           # the number of requests

    # x[i][r] is true when request i stays in room r
    x = [[Bool(f"x_{i}_{r}") for r in range(max_rooms)] for i in range(n_requests)]

    constraints = []

    # Each request stays in exactly one room.
    constraints += [sum(x[i]) == 1 for i in range(n_requests)]

    # A request that already has a room stays in that room.
    for i in range(n_requests):
        if preassigned[i] >= 0:
            constraints.append(x[i][preassigned[i]])

    # A room serves one request at a time. Two stays overlap when each starts before the other
    # ends. A stay ends on its checkout day, so a request that checks out on the day another
    # checks in does not overlap it. Overlapping requests may not share a room.
    for i in range(n_requests):
        for j in range(i + 1, n_requests):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                for r in range(max_rooms):
                    constraints.append(~(x[i][r] & x[j][r]))

    # room_assignments[i] is the room of request i, a number from 0 to max_rooms - 1
    room_assignments = [sum(r * x[i][r] for r in range(max_rooms)) for i in range(n_requests)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"room_assignments": room_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
