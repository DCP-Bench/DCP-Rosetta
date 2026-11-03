# wolf_goat_cabbage: a PySAT (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from pysat.formula import CNF, IDPool


def create_model(instance):
    """A farmer ferries a wolf, a goat and a cabbage across a river in a boat that carries
    the farmer and at most one item. Left alone together, the wolf eats the goat and the goat
    eats the cabbage. Find the stages of a crossing in which nothing is eaten."""
    stage = instance["stage"]  # the number of stages, including the first and the last

    pool = IDPool()  # gives each position below its own variable

    # At each stage, an item or the boat is on the destination shore when true, and on the
    # starting shore when false.
    wolf_pos = [pool.id(("wolf", i)) for i in range(stage)]
    goat_pos = [pool.id(("goat", i)) for i in range(stage)]
    cabbage_pos = [pool.id(("cabbage", i)) for i in range(stage)]
    boat_pos = [pool.id(("boat", i)) for i in range(stage)]

    cnf = CNF()  # the constraints of the crossing

    # Everything starts on the starting shore ...
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        cnf.append([-pos[0]])
    # ... and ends on the destination shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        cnf.append([pos[stage - 1]])

    # The farmer's boat crosses the river at every stage, so its shore changes from one stage
    # to the next.
    for i in range(1, stage):
        cnf.append([boat_pos[i], boat_pos[i - 1]])
        cnf.append([-boat_pos[i], -boat_pos[i - 1]])

    for i in range(stage):
        # The wolf is never left alone with the goat: when both are on one shore, the farmer's
        # boat is on that shore too.
        cnf.append([-goat_pos[i], -wolf_pos[i], boat_pos[i]])
        cnf.append([goat_pos[i], wolf_pos[i], -boat_pos[i]])
        # The goat is never left alone with the cabbage, in the same way.
        cnf.append([-goat_pos[i], -cabbage_pos[i], boat_pos[i]])
        cnf.append([goat_pos[i], cabbage_pos[i], -boat_pos[i]])

    # The boat carries at most one item per crossing: between two consecutive stages, at most
    # one of the wolf, the goat and the cabbage changes shore.
    for i in range(stage - 1):
        # moved[k] is true when item k changes shore between stage i and stage i + 1
        moved = []
        for who, pos in (("wolf", wolf_pos), ("goat", goat_pos), ("cabbage", cabbage_pos)):
            change = pool.id(("moved", who, i))
            cnf.append([-change, pos[i], pos[i + 1]])
            cnf.append([-change, -pos[i], -pos[i + 1]])
            cnf.append([change, -pos[i], pos[i + 1]])
            cnf.append([change, pos[i], -pos[i + 1]])
            moved.append(change)
        for a in range(3):
            for b in range(a + 1, 3):
                cnf.append([-moved[a], -moved[b]])

    return cnf, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
