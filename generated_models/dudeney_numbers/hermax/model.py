# dudeney_numbers: a hermax (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install hermax`):
#   python dudeney_numbers.py dudeney_numbers.json

from hermax.model import Model


def create_model(instance):
    """Find a Dudeney number larger than 1: a perfect cube whose digits add up to the
    cube root of the number. The number has at most n decimal digits."""
    n = instance["n"]  # n: the maximum number of decimal digits of the answer

    # The answer is below 10**n, so its cube root is at most the largest k with k**3 < 10**n.
    limit = 10 ** n - 1
    cap = 2
    while (cap + 1) ** 3 <= limit:
        cap += 1

    m = Model()

    # root is the cube root k of the answer; k = 1 gives the number 1, which is excluded
    root = m.int("root", 2, cap)
    # number is the Dudeney number itself, with at most n digits
    number = m.int("number", 8, cap ** 3)
    # digit[i] is the digit of the answer in place 10**i
    digits = m.int_vector("digit", n, 0, 9)

    # The number is a perfect cube: (root, number) is one of the pairs (k, k**3).
    cubes = [(k, k ** 3) for k in range(2, cap + 1)]
    m &= m.table([root, number], allowed=cubes)

    # The digits of the number, weighted by their place value, make up the number.
    m &= (number == sum(10 ** i * digits[i] for i in range(n)))

    # Dudeney condition: the sum of the digits equals the cube root.
    m &= (sum(digits) == root)

    return m, {"number": number}


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
