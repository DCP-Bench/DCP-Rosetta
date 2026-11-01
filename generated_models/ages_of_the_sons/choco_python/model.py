# ages_of_the_sons: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install pychoco numpy`) with:
#   python ages_of_the_sons.py

from pychoco.model import Model


def create_model(instance):
    """Three sons have ages whose product is 36. Their sum does not settle the ages,
    but knowing that the oldest son has no twin does. Find the ages, oldest first."""
    model = Model()

    # The sons' ages, oldest first.
    a = [model.intvar(0, 36, name=f"A{i + 1}") for i in range(3)]
    # Another triple of ages, oldest first, that fits the same sum.
    b = [model.intvar(0, 36, name=f"B{i + 1}") for i in range(3)]

    # The oldest son has no twin, so his age is above the middle son's.
    model.arithm(a[0], ">", a[1]).post()
    model.arithm(a[1], ">=", a[2]).post()
    # The other triple is listed oldest first too.
    model.arithm(b[0], ">=", b[1]).post()
    model.arithm(b[1], ">=", b[2]).post()

    # The product of the ages in each triple is 36. The fixed value sits in the domain.
    product = model.intvar(36, 36, name="product")
    for ages, tag in ((a, "A"), (b, "B")):
        # The product of the two oldest ages of the triple.
        pair = model.intvar(0, 36, name=f"{tag}12")
        model.times(ages[0], ages[1], pair).post()
        model.times(pair, ages[2], product).post()

    # The other triple has the same sum as the sons.
    model.scalar(a + b, [1, 1, 1, -1, -1, -1], "=", 0).post()
    # Its oldest age differs from the sons' oldest.
    model.arithm(a[0], "!=", b[0]).post()

    return model, {"A1": a[0], "A2": a[1], "A3": a[2]}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
