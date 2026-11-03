# general_store: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python general_store.py

from pyscipopt import Model, quicksum
import numpy as np


def create_model(instance):
    """The owner of a general store has written sixteen words to add up to
    ALL WOOL. Each different letter stands for a different digit: find the
    digit of each letter so that the sixteen words add up to ALL WOOL.

    The instance file is empty ([]): the statement fixes all the data, so
    the instance argument is not read."""
    model = Model("general_store")

    # The ten letters, as the row numbers of the assignment matrix below.
    A, B, C, E, H, L, O, P, S, W = range(10)

    # x[l, v] is 1 when letter l stands for digit v, and 0 when not.
    x = model.addMatrixVar((10, 10), vtype="B", name="x")
    # Each letter stands for exactly one digit.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # Each digit is stood for by at most one letter. There are ten letters
    # and ten digits, so every digit is then stood for by exactly one letter.
    model.addMatrixCons(x.sum(axis=0) <= 1)

    # digit[l] is the digit that letter l stands for.
    digit = x @ np.arange(10)

    def number(letters):
        """The whole number spelled by these letters, most significant first."""
        return quicksum(10**k * digit[l] for k, l in enumerate(reversed(letters)))

    # The sixteen words, as the statement writes them, and their sum ALL WOOL.
    addends = [
        number([C, H, E, S, S]),              # CHESS
        number([C, A, S, H]),                 # CASH
        number([B, O, W, W, O, W]),           # BOWWOW
        number([C, H, O, P, S]),              # CHOPS
        number([A, L, S, O, P, S]),           # ALSOPS
        number([P, A, L, E, A, L, E]),        # PALEALE
        number([C, O, O, L]),                 # COOL
        number([B, A, S, S]),                 # BASS
        number([H, O, P, S]),                 # HOPS
        number([A, L, E, S]),                 # ALES
        number([H, O, E, S]),                 # HOES
        number([A, P, P, L, E, S]),           # APPLES
        number([C, O, W, S]),                 # COWS
        number([C, H, E, E, S, E]),           # CHEESE
        number([C, H, S, O, A, P]),           # CHSOAP
        number([S, H, E, E, P]),              # SHEEP
    ]
    total = number([A, L, L, W, O, O, L])     # ALL WOOL

    # The sixteen words add up to ALL WOOL.
    model.addCons(quicksum(addends) == total)

    # There is no objective: the statement asks only for the digits.
    return model, {
        "A": digit[A], "B": digit[B], "C": digit[C], "E": digit[E], "H": digit[H],
        "L": digit[L], "O": digit[O], "P": digit[P], "S": digit[S], "W": digit[W],
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
