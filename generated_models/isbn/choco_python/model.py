# isbn: a Choco-solver (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python isbn.py isbn.json

from pychoco.model import Model


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid. It starts with
    978 or 979, and its last digit is the check digit: the first 12 digits are multiplied
    alternately by 1 and 3, the products are summed, and the check digit is
    (10 - (sum % 10)) % 10."""
    isbn_init = instance["isbn_init"]  # the 13 digits, with -1 for an unknown digit
    n_digits = len(isbn_init)

    model = Model()

    # isbn[i] is digit i of the ISBN. The first digit is 9, the second 7, and the third 8 or 9.
    isbn = [model.intvar(9, 9, name="isbn_0"), model.intvar(7, 7, name="isbn_1"),
            model.intvar(8, 9, name="isbn_2")]
    isbn += [model.intvar(0, 9, name=f"isbn_{i}") for i in range(3, n_digits)]

    # The known digits keep their value.
    for i in range(n_digits):
        if isbn_init[i] != -1:
            model.arithm(isbn[i], "=", isbn_init[i]).post()

    # weights[i] is the factor for digit i: 1 and 3 alternately, starting with 1.
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits - 1)]
    # The sum of the first 12 digits, each times its factor.
    weighted_sum = model.intvar(0, 9 * sum(weights), name="weighted_sum")
    model.scalar(isbn[:n_digits - 1], weights, "=", weighted_sum).post()
    # The remainder of that sum after division by 10.
    remainder = model.intvar(0, 9, name="remainder")
    model.mod(weighted_sum, 10, remainder).post()
    # 10 minus the remainder.
    complement = model.intvar(1, 10, name="complement")
    model.arithm(remainder, "+", complement, "=", 10).post()
    # The check digit is the complement modulo 10, so a complement of 10 gives 0.
    model.mod(complement, 10, isbn[n_digits - 1]).post()

    return model, {"isbn": isbn}, None


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
