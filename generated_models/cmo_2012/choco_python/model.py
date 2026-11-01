# cmo_2012: a Choco-solver (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python cmo_2012.py cmo_2012.json

from pychoco.model import Model


def primes_below(limit):
    """All primes less than limit, by trial division."""
    result = []
    for k in range(2, limit):
        if all(k % d != 0 for d in range(2, int(k ** 0.5) + 1)):
            result.append(k)
    return result


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number and a * b is a
    perfect square n^2, find the smallest value of a no less than a given minimum. Also,
    b should be larger than 0."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value any of the numbers may take

    primes = primes_below(max_val)  # the primes below max_val

    model = Model()

    # a is the larger number
    a = model.intvar(min_a, max_val, name="a", bounded_domain=True)
    # b is the smaller number
    b = model.intvar(1, max_val, name="b", bounded_domain=True)
    # n is the square root of a * b
    n = model.intvar(0, max_val, name="n", bounded_domain=True)
    # p is the prime a - b
    p = model.intvar(primes, name="p")

    # a is not smaller than b.
    model.arithm(a, ">=", b).post()
    # a - b is the prime p.
    model.arithm(a, "-", b, "=", p).post()

    # the product a * b
    product = model.intvar(0, max_val * max_val, name="product", bounded_domain=True)
    # a * b is a perfect square.
    model.times(a, b, product).post()
    model.square(product, n).post()

    # Minimise a.
    return model, {"a": a, "b": b, "n": n, "p": p}, {"objective": a, "maximize": False}


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
