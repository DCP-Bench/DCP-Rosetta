# cur_num: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install hermax`) with:
#   python cur_num.py
from hermax.model import Model


def create_model(instance):
    """Find a number, from 1 to 10000, other than 48, that has the peculiarity: adding 1 to it
    gives a square number, and adding 1 to its half also gives a square number.

    The statement fixes all the data, so the instance (an empty object) is not read."""
    m = Model()

    # peculiar: the number to print, from 1 to 10000
    peculiar = m.int("peculiar", 1, 10000)
    # root_plus_one: the root r such that peculiar + 1 = r * r (roots 2..100, since 100 * 100 - 1 = 9999)
    root_plus_one = m.int("root_plus_one", 2, 100)
    # root_half_plus_one: the root s such that peculiar / 2 + 1 = s * s (roots 2..70, since 2 * (70 * 70 - 1) = 9798)
    root_half_plus_one = m.int("root_half_plus_one", 2, 70)

    # Rows (root, peculiar) where peculiar + 1 is the square of the root.
    square_rows = [(r, r * r - 1) for r in range(2, 101)]
    # Rows (root, peculiar) where peculiar is twice a number c with c + 1 the square of the root.
    half_rows = [(s, 2 * (s * s - 1)) for s in range(2, 71)]

    # The number plus one is a square.
    m &= m.table([root_plus_one, peculiar], allowed=square_rows)
    # The half of the number plus one is a square (the number is even, so the half is exact).
    m &= m.table([root_half_plus_one, peculiar], allowed=half_rows)
    # Print another number: 48 is the example given in the statement.
    m &= (peculiar != 48)

    # No cost to minimise: any number with the peculiarity will do.
    return m, {"peculiar": peculiar}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
