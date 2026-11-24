# curious_set_of_integers: a CPLEX (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python curious_set_of_integers.py curious_set_of_integers.json

import math
from docplex.mp.model import Model


def create_model(instance):
    """Curious set of integers (Martin Gardner): in the set 1, 3, 8, 120 the product of any two
    members is one less than a perfect square. Find a fifth number, at least 0, that keeps this
    property."""
    n = instance["n"]              # number of members of the final set
    max_val = instance["max_val"]  # the largest value the new number may take
    known = [1, 3, 8, 120]  # the four members given in the statement
    if n != len(known) + 1:
        raise ValueError("the problem adds exactly one number to the four known ones")

    model = Model("curious_set_of_integers")

    # number is the fifth member of the set
    number = model.integer_var(0, max_val, name="number")

    # All members are different: the new number is none of the known ones.
    for k in known:
        model.add(number != k)

    # For each known member k, k * number + 1 is a square p * p.
    # Since number <= max_val, p is at most isqrt(k * max_val + 1). CPLEX refuses p * p, so
    # p is written in binary, p = sum 2^i bit_i, and p * p = sum_i sum_j 2^(i+j) bit_i bit_j,
    # where each product of two bits is a binary that is 1 exactly when both bits are.
    for k in known:
        hi = math.isqrt(k * max_val + 1)
        width = hi.bit_length()
        bit = [model.binary_var(name=f"root_{k}_bit_{i}") for i in range(width)]
        model.add_constraint(model.sum(2 ** i * bit[i] for i in range(width)) <= hi)
        square_terms = []
        for i in range(width):
            square_terms.append(2 ** (2 * i) * bit[i])
            for j in range(i + 1, width):
                both = model.binary_var(name=f"root_{k}_bits_{i}_{j}")
                model.add_constraint(both <= bit[i])
                model.add_constraint(both <= bit[j])
                model.add_constraint(both >= bit[i] + bit[j] - 1)
                square_terms.append(2 * 2 ** (i + j) * both)
        # The product of k and the new number is one less than this square.
        model.add_constraint(k * number + 1 == model.sum(square_terms))

    return model, {"number": number}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
