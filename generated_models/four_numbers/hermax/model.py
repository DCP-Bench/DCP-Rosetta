# four_numbers: a hermax (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install hermax`):
#   python four_numbers.py four_numbers.json

from itertools import product

from hermax.model import Model


def create_model(instance):
    """Find three integers between 1 and 10 such that every given number is the sum of some
    subset of the three. The given numbers are distinct integers between 1 and 10 (up to four
    of them). The answer is the list x of the three integers. There is no objective: any x
    that works is a solution."""
    numbers = instance["numbers"]  # numbers: the given numbers, each must be a subset sum of x (how many varies by instance)
    n = 3                          # n: how many integers are to be found (the problem fixes three)

    m = Model()
    # x[j] is the j-th of the three integers to find, between 1 and 10
    x = m.int_vector("x", n, 1, 10)
    x_vars = [x[j] for j in range(n)]

    # Every given number is the sum of some subset of x. Each subset is a 0/1 mask over the
    # three integers; a mask picks the integers it marks with 1 and adds them up.
    subsets = list(product((0, 1), repeat=n))
    # The triples of 1..10 that are allowed for one given number: those where some subset
    # adds up to it. The triples are enumerated from the problem's bounds, not from the answer.
    all_triples = list(product(range(1, 11), repeat=n))

    # Each given number gets one table constraint: (x[0], x[1], x[2]) must be one of its allowed triples.
    for target in numbers:
        allowed = [triple for triple in all_triples
                   if any(sum(v for v, used in zip(triple, mask) if used) == target
                          for mask in subsets)]
        m &= m.table(x_vars, allowed=allowed)

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
