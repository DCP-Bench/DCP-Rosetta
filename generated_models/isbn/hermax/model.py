# isbn: a hermax (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install hermax`):
#   python isbn.py isbn.json

from hermax.model import Model


def create_model(instance):
    """ISBN-13 check digit completion: the digits marked -1 in the given 13 digits are
    unknown and must be filled in so that the 13 digits form a valid ISBN-13. The number
    must start with 978 or 979, and its weighted digit sum (weights 1, 3, 1, 3, ... from
    the left) must be a multiple of 10, which makes the last digit the check digit."""
    isbn_init = instance["isbn_init"]  # isbn_init[i]: the i-th digit of the ISBN, or -1 if unknown
    n = len(isbn_init)                 # the number of digits (13)

    m = Model()

    # isbn[i] is the i-th digit of the completed ISBN (the declared output)
    isbn = m.int_vector("isbn", n, 0, 9)

    # The digits that are given keep their value.
    for i in range(n):
        if isbn_init[i] != -1:
            m &= (isbn[i] == isbn_init[i])

    # The ISBN starts with 978 or 979: the first digit is 9, the second 7, the third 8 or 9.
    m &= (isbn[0] == 9)
    m &= (isbn[1] == 7)
    m &= (isbn[2] >= 8)

    # Digits are weighted 1, 3, 1, 3, ... from the left.
    weight = [1 if i % 2 == 0 else 3 for i in range(n)]

    # tens is the quotient of the weighted sum by 10. The weighted sum can be at most
    # 9 times the total weight, so tens is bounded by that over 10.
    tens = m.int("tens", 0, (9 * sum(weight)) // 10)

    # The weighted digit sum is a multiple of 10 (the check digit rule).
    m &= (sum(weight[i] * isbn[i] for i in range(n)) == 10 * tens)

    return m, {"isbn": isbn}


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
