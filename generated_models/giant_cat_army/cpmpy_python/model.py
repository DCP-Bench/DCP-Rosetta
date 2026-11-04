# giant_cat_army: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install cpmpy`) with:
#   python giant_cat_army.py

import cpmpy as cp


def create_model(instance):
    """Build a list that starts with [0], where each next element is the previous one
    plus 5, plus 7, or its square root. The elements are distinct integers of at most
    60, the list has 24 elements, ends with 14, and has 2 before 10. The statement
    fixes all the data, so the instance is not used."""
    max_value = 60  # the largest value an element may take
    n = 24          # the number of elements in the list

    # x[i] is the i-th element of the list
    x = cp.intvar(0, max_value, shape=n, name="x")
    # ix2 and ix10 are the positions of the numbers 2 and 10 in the list
    ix2 = cp.intvar(0, n - 1, name="ix2")
    ix10 = cp.intvar(0, n - 1, name="ix10")

    model = cp.Model()

    # All elements are distinct.
    model.add(cp.AllDifferent(x))

    # The list starts with 0 and ends with 14.
    model.add(x[0] == 0)
    model.add(x[n - 1] == 14)

    # The second element is 5 or 7 (the square root of 0 would repeat 0).
    model.add((x[1] == 5) | (x[1] == 7))

    # Each element comes from the previous one by adding 5, adding 7, or taking the square
    # root (the previous element is the square of the next one).
    for i in range(n - 1):
        model.add((x[i + 1] == x[i] + 5) |
                  (x[i + 1] == x[i] + 7) |
                  (x[i] == x[i + 1] * x[i + 1]))

    # The numbers 2, 10 and 14 appear in this order (14 is the last element already).
    model.add(x[ix2] == 2)
    model.add(x[ix10] == 10)
    model.add(ix2 < ix10)

    return model, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
