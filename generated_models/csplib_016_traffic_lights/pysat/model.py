# csplib_016_traffic_lights: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Set the eight traffic lights of a four-way junction, four vehicle lights and four
    pedestrian lights, so that each road and the next one show a safe combination of states.
    Every other combination is forbidden to prevent accidents."""
    allowed_tuples = instance["allowed_tuples"]  # the safe combinations of (V_i, P_i, V_i+1, P_i+1)

    pool = IDPool()

    # vehicle[i] is the state of the vehicle light V_(i+1): 0 red, 1 red-yellow, 2 green, 3 yellow
    vehicle = [Integer(f"V{i + 1}", 0, 3, vpool=pool) for i in range(4)]
    # pedestrian[i] is the state of the pedestrian light P_(i+1): 0 red, 1 green
    pedestrian = [Integer(f"P{i + 1}", 0, 1, vpool=pool) for i in range(4)]
    engine = IntegerEngine(vars=vehicle + pedestrian, vpool=pool)
    cnf = engine.clausify()

    # Road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4
        lights = [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]]
        # chosen[k] is true when roads i and i + 1 show the k-th safe combination
        chosen = [pool.id(("road", i, "tuple", k)) for k in range(len(allowed_tuples))]
        # Roads i and i + 1 show exactly one safe combination.
        cnf.extend(CardEnc.equals(lits=chosen, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
        # The four lights of roads i and i + 1 take the values of the chosen combination.
        for k, row in enumerate(allowed_tuples):
            for light, value in zip(lights, row):
                cnf.append([-chosen[k], light.equals(value)])

    return cnf, {"lights": vehicle + pedestrian}


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
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
