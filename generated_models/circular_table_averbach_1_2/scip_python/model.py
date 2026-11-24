# circular_table_averbach_1_2: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python circular_table_averbach_1_2.py

from pyscipopt import Model, quicksum

# Row indices of the two matrices below.
X, Y, Z = 0, 1, 2                      # the three players
AMERICAN, ENGLISH, FRENCH = 0, 1, 2    # the three nationalities


def create_model(instance):
    """Three players X, Y and Z, of different nationalities (American, English,
    French), sit around a circular table playing Hearts. Each passed three cards
    to the person on their right. Y passed three hearts to the American, and X
    passed the queen of spades and two diamonds to the person who passed their
    cards to the Frenchwoman. Find the seat of each player and of each
    nationality, with seats numbered 0, 1, 2 so that seat 1 is right of seat 0,
    seat 2 is right of seat 1, and seat 0 is right of seat 2.

    The instance file is empty ([]), so the statement fixes all the data:
    three seats for three players, and the right-hand neighbour of seat s is
    seat (s + 1) % 3. The instance argument is not read."""
    seats = range(3)  # the table has three seats, one per player
    model = Model("circular_table_averbach_1_2")

    # sits[p, s] is 1 when player p sits in seat s.
    sits = model.addMatrixVar((3, 3), vtype="B", name="sits")
    # nation[n, s] is 1 when the person of nationality n sits in seat s.
    nation = model.addMatrixVar((3, 3), vtype="B", name="nation")

    # SCIP has no all-different constraint, so each assignment is a 0/1 matrix in
    # which every row and every column sums to 1: each player has one seat and
    # each seat one player, and likewise for the nationalities.
    model.addMatrixCons(sits.sum(axis=1) == 1)
    model.addMatrixCons(sits.sum(axis=0) == 1)
    model.addMatrixCons(nation.sum(axis=1) == 1)
    model.addMatrixCons(nation.sum(axis=0) == 1)

    # Y passed to the American, so the American sits on Y's right: Y sits in
    # seat s exactly when the American sits in seat (s + 1) % 3.
    right = [(s + 1) % 3 for s in seats]
    model.addMatrixCons(sits[Y, :] == nation[AMERICAN, right])

    # X passed to the person P who passed to the Frenchwoman. X's right neighbour
    # is P, and P's right neighbour is the Frenchwoman: X sits in seat s exactly
    # when the Frenchwoman sits in seat (s + 2) % 3, two seats to the right of s.
    two_right = [(s + 2) % 3 for s in seats]
    model.addMatrixCons(sits[X, :] == nation[FRENCH, two_right])

    # Each output is the seat number of one player or nationality: its 0/1 row
    # weighted by the seat numbers, so it equals the one seat that row marks.
    outputs = {
        "american": quicksum(s * nation[AMERICAN, s] for s in seats),
        "english": quicksum(s * nation[ENGLISH, s] for s in seats),
        "french": quicksum(s * nation[FRENCH, s] for s in seats),
        "x": quicksum(s * sits[X, s] for s in seats),
        "y": quicksum(s * sits[Y, s] for s in seats),
        "z": quicksum(s * sits[Z, s] for s in seats),
    }
    return model, outputs


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
