# cur_num: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install z3-solver numpy`) with:
#   python cur_num.py

import z3


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    limit = 10000  # the numbers considered lie between 1 and this limit

    # The peculiar number to find
    peculiar = z3.Int("peculiar")
    # Half of the peculiar number
    half = z3.Int("half")
    # The peculiar number plus 1, and its square root
    plus_one = z3.Int("plus_one")
    root_plus_one = z3.Int("root_plus_one")
    # Half of the peculiar number plus 1, and its square root
    half_plus_one = z3.Int("half_plus_one")
    root_half_plus_one = z3.Int("root_half_plus_one")

    solver = z3.Solver()

    # Every number involved lies between 1 and the limit.
    solver.add([
        z3.And(v >= 1, v <= limit)
        for v in (peculiar, half, plus_one, root_plus_one, half_plus_one, root_half_plus_one)
    ])

    # The answer is not 48, the known example.
    solver.add(peculiar != 48)

    # Adding 1 to the number gives a square.
    solver.add(plus_one == peculiar + 1)
    solver.add(plus_one == root_plus_one * root_plus_one)

    # Half of the number is a whole number, and adding 1 to that half gives a square.
    solver.add(peculiar == 2 * half)
    solver.add(half_plus_one == half + 1)
    solver.add(half_plus_one == root_half_plus_one * root_half_plus_one)

    return solver, {"peculiar": peculiar}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
