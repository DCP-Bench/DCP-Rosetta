# five_brigands: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install cpmpy`) with:
#   python five_brigands.py

import cpmpy as cp


def create_model(instance):
    """Five brigands, Alfonso, Benito, Carlos, Diego and Esteban, captured
    exactly 200 doubloons altogether. If Alfonso had twelve times as much,
    Benito three times as much, Carlos the same amount, Diego half as much and
    Esteban one third as much, they would still have 200 doubloons altogether.
    No brigand had less than one doubloon. How many had each?"""
    # The puzzle states all its numbers, so the instance holds no data.

    # The number of doubloons each brigand has
    a = cp.intvar(1, 200, name="A")  # Alfonso
    b = cp.intvar(1, 200, name="B")  # Benito
    c = cp.intvar(1, 200, name="C")  # Carlos
    d = cp.intvar(1, 200, name="D")  # Diego
    e = cp.intvar(1, 200, name="E")  # Esteban

    model = cp.Model()
    # Together they have 200 doubloons.
    model.add(a + b + c + d + e == 200)
    # With the changed amounts they still have 200 doubloons. Multiplied by 6,
    # to keep whole numbers: 12A + 3B + C + D/2 + E/3 = 200 becomes
    # 72A + 18B + 6C + 3D + 2E = 1200.
    model.add(72 * a + 18 * b + 6 * c + 3 * d + 2 * e == 1200)

    return model, {"A": a, "B": b, "C": c, "D": d, "E": e}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
