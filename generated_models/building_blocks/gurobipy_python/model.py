# building_blocks: a Gurobi (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python building_blocks.py building_blocks.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Put the letters of the alphabet on blocks, one letter per side of each block, so that
    every word in the list can be spelled, using a different block for each letter of the word."""
    num_blocks = instance["num_blocks"]    # how many blocks there are
    num_sides = instance["num_sides"]      # how many sides each block has, so how many letters it carries
    alphabet = instance["alphabet"]        # the letters that appear on the blocks (all but Q and Z)
    num_letters = instance["num_letters"]  # how many letters are placed: one per letter of alphabet
    words_str = instance["words_str"]      # the words that must be spelled
    letters = range(num_letters)           # letter l is the l-th letter of alphabet
    blocks = range(num_blocks)

    # position[c] is the number of the letter c, so each word becomes a list of letter numbers
    position = {letter: i for i, letter in enumerate(alphabet)}
    words = [[position[c] for c in word] for word in words_str]

    model = gp.Model("building_blocks")

    # on[l, b] is 1 when letter l is on block b, and 0 when not.
    on = model.addVars(letters, blocks, vtype=GRB.BINARY, name="on")

    # Every letter is on exactly one block (on.sum(l, "*") adds on[l, b] over all blocks b).
    model.addConstrs((on.sum(l, "*") == 1 for l in letters), name="letter")

    # The letters of a word lie on different blocks, so each block carries at most one letter of
    # each word. A letter repeated in a word is counted twice, as in the reference.
    model.addConstrs((gp.quicksum(on[l, b] for l in words[w]) <= 1 for w in range(len(words))
                      for b in blocks), name="word")

    # Every block carries exactly num_sides letters, one on each side (on.sum("*", b) adds on[l, b] over all letters l).
    model.addConstrs((on.sum("*", b) == num_sides for b in blocks), name="sides")

    # There is no objective: any arrangement that spells every word is a solution.

    # dice[l] is the block that letter l is on: the sum of b * on[l, b] over b, since exactly one term is 1.
    return model, {"dice": [gp.quicksum(b * on[l, b] for b in blocks) for l in letters]}


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
