# cur_num: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install cpmpy`) with:
#   python cur_num.py

import cpmpy as cp


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    # The puzzle states all its numbers, so the instance holds no data.

    # The peculiar number
    peculiar = cp.intvar(1, 10000, name="peculiar")
    # The square roots of peculiar + 1 and of half of peculiar, plus 1
    root_whole = cp.intvar(1, 10000, name="root_whole")
    root_half = cp.intvar(1, 10000, name="root_half")
    # Half of the peculiar number
    half = cp.intvar(1, 10000, name="half")

    model = cp.Model()
    # It is not 48, the known example.
    model.add(peculiar != 48)
    # Adding 1 to it gives a square number.
    model.add(peculiar + 1 == root_whole * root_whole)
    # Adding 1 to its half gives a square number too.
    model.add(peculiar == 2 * half)
    model.add(half + 1 == root_half * root_half)

    return model, {"peculiar": peculiar}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
