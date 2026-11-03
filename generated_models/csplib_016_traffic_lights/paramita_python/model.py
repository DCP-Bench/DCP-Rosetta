# csplib_016_traffic_lights: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights. Choose a
    state for every light so that each pair of neighbouring roads shows one of the safe
    combinations of states."""
    allowed_tuples = instance["allowed_tuples"]  # the safe combinations (V_i, P_i, V_i+1, P_i+1) of light states
    n_roads = 4                 # the roads at the junction; road 4 is followed by road 1
    n_vehicle_states = 4        # vehicle light states: red, red-yellow, green, yellow
    n_pedestrian_states = 2     # pedestrian light states: red, green

    # vehicle[i][s] is true when the vehicle light of road i is in state s
    vehicle = [[Bool(f"vehicle_{i}_{s}") for s in range(n_vehicle_states)] for i in range(n_roads)]
    # pedestrian[i][s] is true when the pedestrian light of road i is in state s
    pedestrian = [[Bool(f"pedestrian_{i}_{s}") for s in range(n_pedestrian_states)] for i in range(n_roads)]

    # Each light is in exactly one state.
    constraints = [sum(vehicle[i]) == 1 for i in range(n_roads)] + [sum(pedestrian[i]) == 1 for i in range(n_roads)]

    # Each road with the next one shows one of the safe combinations.
    for i in range(n_roads):
        j = (i + 1) % n_roads
        # chosen[t] is true when roads i and j show the safe combination t
        chosen = [Bool(f"chosen_{i}_{t}") for t in range(len(allowed_tuples))]
        constraints.append(sum(chosen) == 1)
        for t, (v1, p1, v2, p2) in enumerate(allowed_tuples):
            constraints.append(If(chosen[t], And([vehicle[i][v1], pedestrian[i][p1], vehicle[j][v2], pedestrian[j][p2]])))

    # The lights, in the order V1 to V4 and then P1 to P4, each as its state number.
    lights = [sum(s * vehicle[i][s] for s in range(n_vehicle_states)) for i in range(n_roads)]
    lights += [sum(s * pedestrian[i][s] for s in range(n_pedestrian_states)) for i in range(n_roads)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"lights": lights}


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
