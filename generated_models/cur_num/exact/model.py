# cur_num: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install exact numpy`) with:
#   python cur_num.py

from exact import Exact


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    solver = Exact()

    # Exact identifies its variables by name.
    # The number to find, between 1 and 10000
    solver.addVariable("peculiar", 1, 10000)
    # The number plus 1, which must be a square
    solver.addVariable("plus_one", 1, 10000)
    # The square root of plus_one, at most 100 since plus_one is at most 10000
    solver.addVariable("root_of_plus_one", 1, 100)
    # Half of the number
    solver.addVariable("half", 1, 10000)
    # Half of the number plus 1, which must be a square
    solver.addVariable("half_plus_one", 1, 10000)
    # The square root of half_plus_one, at most 100 since half_plus_one is at most 10000
    solver.addVariable("root_of_half_plus_one", 1, 100)

    # Adding 1 to the number gives a square number.
    solver.addConstraint([(1, "plus_one"), (-1, "peculiar")], True, 1, True, 1)
    solver.addMultiplication(["root_of_plus_one", "root_of_plus_one"], True, "plus_one", True, "plus_one")

    # half is half of the number.
    solver.addConstraint([(1, "peculiar"), (-2, "half")], True, 0, True, 0)

    # Adding 1 to half gives a square number.
    solver.addConstraint([(1, "half_plus_one"), (-1, "half")], True, 1, True, 1)
    solver.addMultiplication(["root_of_half_plus_one", "root_of_half_plus_one"], True, "half_plus_one", True, "half_plus_one")

    # above is 1 when the number is 49 or more, and below is 1 when the number is 47 or less.
    solver.addVariable("above", 0, 1)
    solver.addVariable("below", 0, 1)
    solver.addReification("above", True, [(1, "peculiar")], 49)
    solver.addReification("below", True, [(-1, "peculiar")], -47)

    # The number is not 48, which the puzzle already gives.
    solver.addConstraint([(1, "above"), (1, "below")], True, 1)

    return solver, {"peculiar": "peculiar"}


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
