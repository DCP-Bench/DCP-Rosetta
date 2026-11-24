# kakuro: a SCIP (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python kakuro.py kakuro.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Kakuro: write a digit from 1 to 9 into each white cell of a square grid so that
    every run of white cells (a segment) adds up to its clue and no digit repeats in a
    segment. Black cells are printed as 0. The clues are given, nothing is maximised."""
    n = instance["n"]              # the grid has n rows and n columns
    blanks = instance["blanks"]    # [r, c], 1-based: the black cells, which hold no digit
    segments = instance["problem"] # [clue, [r, c], [r, c], ...] per run, 1-based cells
    # The instance also has num_blanks and num_p: the lengths of blanks and segments, not needed here.

    # Work with 0-based (row, column) pairs from here on.
    black = {(r - 1, c - 1) for r, c in blanks}
    white = [(r, c) for r in range(n) for c in range(n) if (r, c) not in black]
    digits = range(1, 10)  # the digits a white cell may hold: 1 to 9 inclusive

    model = Model("kakuro")

    # x[r, c] is the digit written in row r, column c of the grid, 0 for a black cell.
    # The bounds 0 to 9 come from the statement; the cell values are fixed below.
    x = model.addMatrixVar((n, n), vtype="I", lb=0, ub=9, name="x")

    # y[r, c, v] is 1 when white cell (r, c) holds the digit v, and 0 when not.
    # One-hot binaries: they let each digit be counted within a segment, which is what
    # "no digit is duplicated" needs. A pairwise != would be far weaker.
    y = {(r, c, v): model.addVar(vtype="B", name=f"y_{r}_{c}_{v}")
         for (r, c) in white for v in digits}

    # Black cells hold no digit: their printed value is 0.
    for (r, c) in black:
        model.addCons(x[r, c] == 0)

    # Each white cell holds exactly one digit, and its printed value is that digit.
    for (r, c) in white:
        model.addCons(quicksum(y[r, c, v] for v in digits) == 1)
        model.addCons(x[r, c] == quicksum(v * y[r, c, v] for v in digits))

    # Each segment (a run of white cells read across or down) adds up to its clue.
    # Its cells must hold different digits: each digit is used at most once in the run.
    for segment in segments:
        clue = segment[0]  # the sum the run must add up to
        cells = [(r - 1, c - 1) for r, c in segment[1:]]  # the white cells of the run
        model.addCons(quicksum(x[r, c] for r, c in cells) == clue)
        for v in digits:
            # no digit is duplicated in this run
            model.addCons(quicksum(y[r, c, v] for r, c in cells) <= 1)

    # No objective: a satisfaction problem, any grid meeting every clue is an answer.
    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
