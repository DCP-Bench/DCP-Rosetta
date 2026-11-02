# ages_of_the_sons: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install z3-solver numpy`) with:
#   python ages_of_the_sons.py

import z3


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    # The puzzle states its own product, so the instance holds no data.

    # a[i] is the age of the i-th son, oldest first.
    a = [z3.Int(f"A{i + 1}") for i in range(3)]
    # b is another triple of ages, oldest first, that the mathematician cannot rule out.
    b = [z3.Int(f"B{i + 1}") for i in range(3)]

    solver = z3.Solver()

    # Ages are between 0 and 36.
    solver.add([z3.And(0 <= age, age <= 36) for age in a + b])

    # The oldest son is strictly older than the middle son, and the middle son is at
    # least as old as the youngest.
    solver.add(a[0] > a[1])
    solver.add(a[1] >= a[2])

    # The product of the sons' ages is 36.
    solver.add(a[0] * a[1] * a[2] == 36)

    # The other triple is ordered the same way and also has product 36.
    solver.add(b[0] >= b[1])
    solver.add(b[1] >= b[2])
    solver.add(b[0] * b[1] * b[2] == 36)

    # The other triple has the same sum of ages as the sons, but a different oldest age.
    solver.add(z3.Sum(b) == z3.Sum(a))
    solver.add(b[0] != a[0])

    return solver, {"A1": a[0], "A2": a[1], "A3": a[2]}


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
