# csplib_001_car_sequencing: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Car sequencing: cars of several types are put in an order on an assembly line.
    Each option station can handle only a limited number of cars in any stretch of
    consecutive cars, so the cars that need an option must be spread out."""
    demand = instance["demand"]        # demand[t]: number of cars of type t to build
    requires = instance["requires"]    # requires[t][o]: cars of type t need option o
    at_most = instance["at_most"]      # at_most[o]: most cars needing option o in one stretch
    per_slots = instance["per_slots"]  # per_slots[o]: length of the stretch for option o

    n_types = len(demand)
    n_opts = len(at_most)
    n_cars = sum(demand)  # one position on the line for each car

    # car[p][t] is true when the car at position p of the line is of type t
    car = [[Bool(f"car_{p}_{t}") for t in range(n_types)] for p in range(n_cars)]

    constraints = []

    # Each position of the line holds exactly one car.
    constraints += [sum(car[p]) == 1 for p in range(n_cars)]
    # Each car type appears on the line as often as its demand.
    constraints += [sum(car[p][t] for p in range(n_cars)) == demand[t] for t in range(n_types)]

    # needs[p][o] is 1 when the car at position p needs option o, and 0 otherwise.
    needs = [[sum(car[p][t] for t in range(n_types) if requires[t][o]) for o in range(n_opts)]
             for p in range(n_cars)]

    # In every stretch of per_slots[o] consecutive positions, at most at_most[o] cars need option o.
    for o in range(n_opts):
        # An option that no car type needs has nothing to limit.
        if not any(requires[t][o] for t in range(n_types)):
            continue
        for start in range(n_cars - per_slots[o] + 1):
            constraints.append(
                sum(needs[p][o] for p in range(start, start + per_slots[o])) <= at_most[o])

    # sequence[p]: the type of the car at position p, counted from 0.
    sequence = [sum(t * car[p][t] for t in range(1, n_types)) for p in range(n_cars)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"sequence": sequence}


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
