# building_blocks: a SCIP (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python building_blocks.py building_blocks.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Place the letters of the alphabet on blocks so that every word in the list
    can be spelled. Each block has one letter on each of its sides, and the
    blocks together carry every letter once. The letters of one word go on
    different blocks, one letter per block. dice[i] is the number of the block
    (0 to num_blocks - 1, as the statement numbers them) that carries alphabet[i]."""
    alphabet = instance["alphabet"]        # the letters to place; dice[i] is for alphabet[i]
    num_letters = instance["num_letters"]  # the number of letters to place, the length of alphabet
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides, and so letters, on each block
    words = instance["words_str"]          # the words that have to be spellable

    model = Model("building_blocks")

    # on[i, k] is 1 when letter i is on block k, and 0 when not. Each letter is
    # on one side of one block, so the choice is one block per letter.
    on = model.addMatrixVar((num_letters, num_blocks), vtype="B", name="on")

    # Each letter is on exactly one block.
    model.addMatrixCons(on.sum(axis=1) == 1)

    # Each block has num_sides sides, each with one letter, so it carries num_sides letters.
    model.addMatrixCons(on.sum(axis=0) == num_sides)

    # Spelling a word takes one side per letter, and two sides of one block cannot
    # both show. count[w, i] is how often alphabet[i] occurs in word w, so the sum
    # counts every occurrence: a block carries at most one letter occurrence per word.
    count = np.array([[word.count(letter) for letter in alphabet] for word in words])
    model.addMatrixCons(count @ on <= 1)

    # dice[i] is the block number of letter i: the k with on[i, k] = 1, as a sum that
    # uses only the one-hot choice, so no extra integer variable is needed.
    dice = (on * np.arange(num_blocks)).sum(axis=1)

    return model, {"dice": dice}


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
