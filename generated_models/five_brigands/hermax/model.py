# five_brigands: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install hermax`) with:
#   python five_brigands.py

from hermax.model import Model


def create_model(instance):
    """The five brigands Alfonso, Benito, Carlos, Diego and Esteban hold exactly 200 doubloons
    in all. Had Alfonso twelve times as much, Benito three times as much, Carlos the same,
    Diego half as much and Esteban one-third as much, the total would still be 200.
    Each brigand has at least one doubloon. Find how many doubloons each one has.

    The statement fixes all the data, so the instance argument is not read.
    """
    m = Model()

    # A, B, C, D, E: doubloons held by Alfonso, Benito, Carlos, Diego and Esteban; each at least 1.
    # Upper bounds come from the other four holding at least one each (D at least 2 and E at least 3,
    # since D is even and E a multiple of 3), so the multiplied-share equation
    # 12A + 3B + C + D/2 + E/3 = 200 leaves A at most 16, B at most 61 and C at most 183,
    # and the total of 200 leaves D at most 196 and E at most 195.
    A = m.int("A", 1, 16)
    B = m.int("B", 1, 61)
    C = m.int("C", 1, 183)
    D = m.int("D", 2, 196)
    E = m.int("E", 3, 195)

    # Together the five hold exactly 200 doubloons.
    m &= (A + B + C + D + E == 200)

    # Diego's half and Esteban's third must be whole doubloons, so D is even and E is a multiple of 3.
    # d_half = D / 2 and e_third = E / 3 are auxiliary integers that carry those halves and thirds.
    d_half = m.int("d_half", 1, 98)
    e_third = m.int("e_third", 1, 65)
    m &= (D == 2 * d_half)
    m &= (E == 3 * e_third)

    # With the multiplied shares, the total is still 200:
    # 12 * Alfonso + 3 * Benito + Carlos + Diego / 2 + Esteban / 3 = 200.
    m &= (12 * A + 3 * B + C + d_half + e_third == 200)

    # The problem asks for a solution, not an optimum, so the model has no objective.
    return m, {"A": A, "B": B, "C": C, "D": D, "E": E}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
