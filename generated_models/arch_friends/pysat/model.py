# arch_friends: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python arch_friends.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Harriet bought four pairs of shoes at four different stores, one stop each.
    Work out the order in which she bought the pairs and which store each came
    from, so that the clues hold."""
    n_stops = 4  # the stops are numbered 1 to 4, one for each pair and each store
    pool = IDPool()  # gives each variable a number

    # the stop at which each pair was bought
    shoes = [Integer(name, 1, n_stops, vpool=pool)
             for name in ("ecru", "fuchsia", "purple", "suede")]
    ecru, fuchsia, purple, suede = shoes
    # the stop at which each store was visited
    stores = [Integer(name, 1, n_stops, vpool=pool)
              for name in ("footfarm", "heels", "palace", "tootsies")]
    footfarm, heels, palace, tootsies = stores
    engine = IntegerEngine(vars=shoes + stores, vpool=pool)

    # Each pair was bought at a different stop.
    engine.add_alldifferent(shoes)
    # Each store was visited at a different stop.
    engine.add_alldifferent(stores)

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    engine.add_equal(fuchsia, heels)
    # The suede sandals were bought two stops after The Shoe Palace.
    engine.add_linear(palace - suede == -2)

    cnf = engine.clausify()  # the constraints above, with the clues below added to them

    # The store visited just after buying the purple pumps was not Tootsies.
    for v in range(1, n_stops):
        cnf.append([-purple.equals(v), -tootsies.equals(v + 1)])
    # The Foot Farm was the second stop.
    cnf.append([footfarm.equals(2)])

    return cnf, {"ecruespadrilles": ecru, "fuchsiaflats": fuchsia,
                 "purplepumps": purple, "suedesandals": suede,
                 "footfarm": footfarm, "heelsinahandcart": heels,
                 "theshoepalace": palace, "tootsies": tootsies}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
