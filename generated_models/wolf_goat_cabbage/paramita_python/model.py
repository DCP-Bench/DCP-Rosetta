# wolf_goat_cabbage: a Paramita (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, add_to_container, to_cnf

# The things the farmer ferries across: the wolf, the goat and the cabbage.
ITEMS = ["wolf", "goat", "cabbage"]


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and a single item, and if left unattended
    together the wolf eats the goat and the goat eats the cabbage. Find a
    crossing in which nothing is eaten."""
    n_stages = instance["stage"]  # the number of stages, the first being the start and the last the finish

    # pos[it][t] is true when the item is on the destination shore at stage t
    pos = {it: [Bool(f"{it}_pos_{t}") for t in range(n_stages)] for it in ITEMS}
    # boat[t] is true when the boat is on the destination shore at stage t, with the farmer
    boat = [Bool(f"boat_pos_{t}") for t in range(n_stages)]

    constraints = []

    # Everything starts on the starting shore.
    constraints += [~pos[it][0] for it in ITEMS]
    constraints += [~boat[0]]

    # Everything ends on the destination shore.
    constraints += [pos[it][n_stages - 1] for it in ITEMS]
    constraints += [boat[n_stages - 1]]

    # The farmer rows the boat across at every stage, so the boat changes shore each time.
    for t in range(n_stages - 1):
        constraints.append(Iff(boat[t], ~boat[t + 1]))

    # The boat carries the farmer and at most one item. An item crosses when it
    # changes shore, and only from the shore the farmer is on.
    for t in range(n_stages - 1):
        crossings = []  # the items that change shore between stage t and stage t + 1
        for it in ITEMS:
            crosses = Bool(f"{it}_crosses_{t}")  # true when the item changes shore at this crossing
            constraints.append(Iff(crosses, pos[it][t] + pos[it][t + 1] == 1))
            constraints.append(If(crosses, Iff(pos[it][t], boat[t])))
            crossings.append(crosses)
        constraints.append(sum(crossings) <= 1)

    # The wolf would eat the goat, so wherever they share a shore, the farmer is on that shore too.
    for t in range(n_stages):
        constraints.append(If(Iff(pos["wolf"][t], pos["goat"][t]),
                              Iff(boat[t], pos["goat"][t])))

    # The goat would eat the cabbage, so wherever they share a shore, the farmer is on that shore too.
    for t in range(n_stages):
        constraints.append(If(Iff(pos["goat"][t], pos["cabbage"][t]),
                              Iff(boat[t], pos["goat"][t])))

    # the shore of each item and of the boat at each stage
    outputs = {
        "wolf_pos": pos["wolf"],
        "goat_pos": pos["goat"],
        "cabbage_pos": pos["cabbage"],
        "boat_pos": boat,
    }

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


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
