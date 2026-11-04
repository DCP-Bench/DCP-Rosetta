# ages_of_the_sons: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install cpmpy`) with:
#   python ages_of_the_sons.py

import cpmpy as cp


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    # The puzzle states its own product, so the instance holds no data.

    # a[0], a[1], a[2] are the ages of the sons, oldest first
    a = cp.intvar(0, 36, shape=3, name="A")
    # b is another possible triple of ages, also oldest first. It shows why the
    # sum alone was not enough: b has the same product and sum but another oldest.
    b = cp.intvar(0, 36, shape=3, name="B")

    model = cp.Model()
    # The ages are ordered, and the oldest son is strictly older than the next.
    model.add(a[0] > a[1])
    model.add(a[1] >= a[2])
    # The product of the ages is 36.
    model.add(a[0] * a[1] * a[2] == 36)
    # The other triple is ordered too, has the same product and the same sum
    # as the sons' ages, and a different oldest age.
    model.add(b[0] >= b[1])
    model.add(b[1] >= b[2])
    model.add(b[0] * b[1] * b[2] == 36)
    model.add(cp.sum(b) == cp.sum(a))
    model.add(b[0] != a[0])

    return model, {"A1": a[0], "A2": a[1], "A3": a[2]}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
