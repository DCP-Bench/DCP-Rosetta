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
    # 200 is the most any one can hold, since the other four hold at least one each.
    A = m.int("A", 1, 200)
    B = m.int("B", 1, 200)
    C = m.int("C", 1, 200)
    D = m.int("D", 1, 200)
    E = m.int("E", 1, 200)

    # Together the five hold exactly 200 doubloons.
    m &= (A + B + C + D + E == 200)

    # Diego's half and Esteban's third must be whole doubloons, so D is even and E is a multiple of 3.
    # d_half = D / 2 and e_third = E / 3 are auxiliary integers that carry those halves and thirds.
    d_half = m.int("d_half", 0, 100)
    e_third = m.int("e_third", 0, 66)
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
