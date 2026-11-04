# ages_of_the_sons: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install exact numpy`) with:
#   python ages_of_the_sons.py

from exact import Exact


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    product = 36  # the product of the three ages, as the old man says

    solver = Exact()

    # Exact identifies its variables by name.
    # A1, A2 and A3 are the ages of the sons, oldest first.
    # B1, B2 and B3 are the ages of another triple with the same product and sum, oldest first.
    ages = ["A1", "A2", "A3"]
    other = ["B1", "B2", "B3"]
    for name in ages + other:
        solver.addVariable(name, 0, product)

    # The product of the three ages of each triple.
    solver.addVariable("product", product, product)

    # Each triple multiplies to the product, computed as (first * second) * third.
    for prefix, names in (("A", ages), ("B", other)):
        pair = f"{prefix}_first_two"  # the product of the first two ages of the triple
        solver.addVariable(pair, 0, product * product)
        solver.addMultiplication([names[0], names[1]], True, pair, True, pair)
        solver.addMultiplication([pair, names[2]], True, "product", True, "product")

    # The sons' oldest is strictly older than the second son; the younger two may be twins.
    solver.addConstraint([(1, "A1"), (-1, "A2")], True, 1)
    solver.addConstraint([(1, "A2"), (-1, "A3")], True, 0)

    # The other triple is also listed oldest first, and its top two may be twins.
    solver.addConstraint([(1, "B1"), (-1, "B2")], True, 0)
    solver.addConstraint([(1, "B2"), (-1, "B3")], True, 0)

    # The other triple has the same sum of ages as the sons.
    solver.addConstraint([(1, name) for name in ages] + [(-1, name) for name in other], True, 0, True, 0)

    # older is 1 exactly when the oldest son is older than the other triple's oldest.
    # younger is 1 exactly when the other triple's oldest is older than the oldest son.
    solver.addVariable("older", 0, 1)
    solver.addVariable("younger", 0, 1)
    solver.addReification("older", True, [(1, "A1"), (-1, "B1")], 1)
    solver.addReification("younger", True, [(1, "B1"), (-1, "A1")], 1)

    # The other triple's oldest son is a different age from the sons' oldest.
    solver.addConstraint([(1, "older"), (1, "younger")], True, 1)

    return solver, {name: name for name in ages}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
