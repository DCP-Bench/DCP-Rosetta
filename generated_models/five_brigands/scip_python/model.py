# five_brigands: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python five_brigands.py

from pyscipopt import Model


def create_model(instance):
    """Five brigands, Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E),
    have together exactly 200 doubloons, and each has at least one. If Alfonso had
    twelve times as much, Benito three times, Carlos the same, Diego half as much and
    Esteban one-third as much, the total would still be 200. Find how many doubloons
    each brigand has.

    The instance file is empty ([]): the statement fixes every number, so the
    argument is not read.
    """
    model = Model("five_brigands")

    # A, B, C, D, E: the doubloons held by Alfonso, Benito, Carlos, Diego and Esteban.
    # Lower bound 1: the statement says no brigand had less than one doubloon.
    # Upper bound 196: the other four have at least one each and the total is 200,
    # so no one can have more than 200 - 4 = 196.
    A = model.addVar("A", vtype="I", lb=1, ub=196)
    B = model.addVar("B", vtype="I", lb=1, ub=196)
    C = model.addVar("C", vtype="I", lb=1, ub=196)
    D = model.addVar("D", vtype="I", lb=1, ub=196)
    E = model.addVar("E", vtype="I", lb=1, ub=196)

    # The brigands captured exactly 200 doubloons altogether.
    model.addCons(A + B + C + D + E == 200)

    # With the shares rescaled (Alfonso 12A, Benito 3B, Carlos C, Diego D/2, Esteban E/3),
    # the total is still 200: 12A + 3B + C + D/2 + E/3 == 200.
    # Multiplied by 6 to clear the fractions 1/2 and 1/3, so every coefficient is an
    # integer and the equality holds exactly.
    model.addCons(72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 1200)

    # No objective: any split of the 200 doubloons that meets both totals is an answer.
    return model, {"A": A, "B": B, "C": C, "D": D, "E": E}


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
