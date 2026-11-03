# allergy: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python allergy.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Four friends, Debra, Janet, Hugh and Rick, are each allergic to one of eggs,
    mold, nuts and ragweed, and each has one of the surnames Baxter, Lemon, Malone
    and Fleet. Match every friend to one allergy and one surname, given the clues."""
    n_friends = 4  # four friends, four allergies and four surnames
    debra, janet, hugh, rick = range(n_friends)  # the friends are the values 0 to 3

    pool = IDPool()

    # foods[k] is the friend allergic to food k, for eggs, mold, nuts and ragweed.
    foods = [Integer(f"food{k}", 0, n_friends - 1, vpool=pool) for k in range(n_friends)]
    eggs, mold, nuts, ragweed = foods

    # surnames[k] is the friend with surname k, for Baxter, Lemon, Malone and Fleet.
    surnames = [Integer(f"surname{k}", 0, n_friends - 1, vpool=pool) for k in range(n_friends)]
    baxter, lemon, malone, fleet = surnames

    # Rules on the friends, their allergies and their surnames.
    engine = IntegerEngine(vars=foods + surnames, vpool=pool)

    # Each friend has a different allergy.
    engine.add_alldifferent(foods)

    # Each friend has a different surname.
    engine.add_alldifferent(surnames)

    # Baxter is allergic to eggs.
    engine.add_equal(eggs, baxter)
    cnf = engine.clausify()

    # Rick is not allergic to mold.
    cnf.append([-mold.equals(rick)])

    # Hugh is neither surnamed Lemon nor Fleet.
    cnf.append([-lemon.equals(hugh)])
    cnf.append([-fleet.equals(hugh)])

    # Debra is allergic to ragweed.
    cnf.append([ragweed.equals(debra)])

    # Janet is not surnamed Lemon and is allergic to neither eggs nor mold.
    cnf.append([-lemon.equals(janet)])
    cnf.append([-eggs.equals(janet)])
    cnf.append([-mold.equals(janet)])

    return cnf, {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet,
    }


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
