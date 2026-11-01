# ages_of_the_sons: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install ortools`) with:
#   python ages_of_the_sons.py

from ortools.sat.python import cp_model


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    model = cp_model.CpModel()

    # a[i] is the age of the i-th son, oldest first.
    a = [model.new_int_var(0, 36, f"A{i + 1}") for i in range(3)]
    # b is another possible triple of ages, oldest first.
    b = [model.new_int_var(0, 36, f"B{i + 1}") for i in range(3)]

    # The ages are ordered, and the oldest son is strictly older than the next.
    model.add(a[0] > a[1])
    model.add(a[1] >= a[2])
    # The product of the ages is 36.
    model.add_multiplication_equality(36, a)

    # The other triple is ordered, with the same product and sum as the sons' ages.
    model.add(b[0] >= b[1])
    model.add(b[1] >= b[2])
    model.add_multiplication_equality(36, b)
    model.add(sum(b) == sum(a))
    # Its oldest son is a different age from the sons' oldest.
    model.add(b[0] != a[0])

    return model, {"A1": a[0], "A2": a[1], "A3": a[2]}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
