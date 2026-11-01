# curious_set_of_integers: a Choco-solver (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from pychoco.model import Model


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n_integers = instance["n"]     # the number of integers in the set, the one to find included
    max_val = instance["max_val"]  # the largest value an integer in the set may take

    # The integers given in the statement, which open the set.
    known = [1, 3, 8, 120]

    model = Model()

    # x[i] is the i-th integer of the set; the last one is the number to find
    x = [model.intvar(0, max_val, name=f"x_{i}", bounded_domain=True) for i in range(n_integers)]

    # All integers of the set differ.
    model.all_different(x).post()

    # The first integers of the set are the known ones.
    for i, value in enumerate(known):
        model.arithm(x[i], "=", value).post()

    # The product of any two integers of the set is one less than a perfect square.
    # root is the square root of square, and square is one more than the product.
    for i in range(n_integers):
        for j in range(i + 1, n_integers):
            root = model.intvar(0, max_val, name=f"root_{i}_{j}", bounded_domain=True)
            square = model.intvar(0, max_val * max_val, name=f"square_{i}_{j}", bounded_domain=True)
            model.square(square, root).post()
            if i < len(known):
                # A known integer times x[j], plus 1, is that square.
                model.scalar([square, x[j]], [1, -known[i]], "=", 1).post()
            else:
                # Two integers that are both not known.
                product = model.intvar(0, max_val * max_val, name=f"product_{i}_{j}", bounded_domain=True)
                model.times(x[i], x[j], product).post()
                model.scalar([square, product], [1, -1], "=", 1).post()

    return model, {"number": x[n_integers - 1]}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
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
