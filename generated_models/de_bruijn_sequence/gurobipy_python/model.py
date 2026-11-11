# de_bruijn_sequence: a Gurobi (Python) model from DCP Rosetta.
# Download the `de_bruijn_sequence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python de_bruijn_sequence.py de_bruijn_sequence.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """De Bruijn sequence: a cyclic sequence of base^n symbols in which every string of n symbols
    occurs exactly once as a substring, reading around the cycle where it ends."""
    base = instance["base"]  # the size of the alphabet: the symbols are 0 to base - 1
    n = instance["n"]  # the length of the strings that must each occur once
    m = base ** n  # the length of the sequence, which is also the number of strings of length n
    positions = range(m)  # positions 0 to m - 1 of the cyclic sequence
    symbols = range(base)  # the symbols of the alphabet
    words = range(m)  # the strings of length n, numbered by their base-`base` value, most significant digit first

    model = gp.Model("de_bruijn_sequence")

    # sym[k, d] is 1 when position k of the sequence holds the symbol d.
    sym = model.addVars(positions, symbols, vtype=GRB.BINARY, name="sym")
    # Each position holds exactly one symbol.
    model.addConstrs((sym.sum(k, "*") == 1 for k in positions), name="position")
    # The sequence, read as its symbols in order.
    de_bruijn = [gp.quicksum(d * sym[k, d] for d in symbols) for k in positions]

    # word[i, w] is 1 when the string of length n that starts at position i (wrapping around the end)
    # is the string w.
    word = model.addVars(positions, words, vtype=GRB.BINARY, name="word")
    # Each start position reads exactly one string.
    model.addConstrs((word.sum(i, "*") == 1 for i in positions), name="one_word")
    # Digit j of the string read from position i is the symbol at position (i + j) mod m: for each
    # place j and each symbol d, the strings whose digit at place j is d are exactly those that
    # start where the symbol d sits at place j. This ties each string to the sequence without a big
    # positional sum.
    model.addConstrs((gp.quicksum(word[i, w] for w in words if (w // base ** (n - 1 - j)) % base == d)
                      == sym[(i + j) % m, d]
                      for i in positions for j in range(n) for d in symbols), name="digit")

    # Each string occurs at most once. There are m start positions and m strings, so at most once
    # means exactly once.
    model.addConstrs((word.sum("*", w) <= 1 for w in words), name="distinct")

    return model, {"de_bruijn": de_bruijn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
