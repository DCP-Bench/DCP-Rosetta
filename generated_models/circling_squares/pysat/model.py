# circling_squares: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python circling_squares.py

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Circling the squares: place a different number in each of the ten squares of a circle
    so that the sum of the squares of any two adjacent numbers equals the sum of the squares of
    the two numbers diametrically opposite them. Four numbers are given, and no number needs
    more than two figures."""
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the squares, in order around the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}  # the numbers the puzzle places in squares A, B, F and G
    largest = 99                                # no number needs more than two figures

    pool = IDPool()
    # x[name] is the number placed in that square
    x = {name: Integer(name, 1, largest, vpool=pool) for name in names}
    engine = IntegerEngine(vars=list(x.values()), vpool=pool)

    # The sum of the squares of x1 and x2 equals the sum of the squares of y1 and y2. The squares
    # are tabulated, because the model cannot multiply two unknown numbers. sums[s] is true when
    # the common sum of squares is s, and at most one s can be true.
    def same_sum_of_squares(x1, x2, y1, y2, tag):
        sums = {}
        for first, second in ((x1, x2), (y1, y2)):
            for v1 in range(1, largest + 1):
                for v2 in range(1, largest + 1):
                    s = v1 * v1 + v2 * v2
                    if s not in sums:
                        sums[s] = pool.id(("sum", tag, s))
                    cnf.append([-first.equals(v1), -second.equals(v2), sums[s]])
        cnf.extend(CardEnc.atmost(lits=list(sums.values()), bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # The ten numbers are all different.
    engine.add_alldifferent(list(x.values()))

    # The given numbers stand as they are.
    for name, value in given.items():
        engine.add_linear(x[name] == value)

    cnf = engine.clausify()

    # the numbers in the squares, named as in the puzzle
    A, B, C, D, E, F, G, H, I, K = (x[name] for name in names)
    # Each pair of adjacent squares has the same sum of squares as the two squares opposite it.
    same_sum_of_squares(A, B, F, G, "AB")
    same_sum_of_squares(B, C, G, H, "BC")
    same_sum_of_squares(C, D, H, I, "CD")
    same_sum_of_squares(D, E, I, K, "DE")
    same_sum_of_squares(E, F, K, A, "EF")

    return cnf, {name: x[name] for name in names}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
