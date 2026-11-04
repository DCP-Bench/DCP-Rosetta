# building_blocks: a Python-MIP (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python building_blocks.py building_blocks.json

import mip


def create_model(instance):
    """Alphabet blocks carry one letter on each side, and together they carry every letter
    of the alphabet used. Arranged in some order, the blocks must spell every word of a
    given list. Find which block each letter sits on."""
    n_blocks = instance["num_blocks"]    # the number of blocks
    n_sides = instance["num_sides"]      # the number of sides on each block
    n_letters = instance["num_letters"]  # the number of letters on the blocks
    alphabet = instance["alphabet"]      # the letters on the blocks; a letter's position here names it
    words_str = instance["words_str"]    # the words that must be spelled

    model = mip.Model(solver_name="CBC")

    # on_block[i][b] is 1 when letter i is on block b, and 0 when not
    on_block = [
        [model.add_var(f"on_block_{i}_{b}", var_type=mip.BINARY) for b in range(n_blocks)]
        for i in range(n_letters)
    ]
    # Each letter is on exactly one block.
    for i in range(n_letters):
        model += mip.xsum(on_block[i][b] for b in range(n_blocks)) == 1

    # Every block shows n_sides letters, one per side.
    for b in range(n_blocks):
        model += mip.xsum(on_block[i][b] for i in range(n_letters)) == n_sides

    # dice[i] is the number of the block that letter i sits on, counted from 0
    dice = []
    for i in range(n_letters):
        d = model.add_var(f"dice_{i}", lb=0, ub=n_blocks - 1, var_type=mip.INTEGER)
        model += d == mip.xsum(b * on_block[i][b] for b in range(n_blocks))
        dice.append(d)

    # Each word as the positions of its letters in the alphabet
    words = [[alphabet.index(ch) for ch in word] for word in words_str]
    # A word is spelled with one block per letter, so no block carries two of its letters.
    for letters in words:
        for b in range(n_blocks):
            model += mip.xsum(on_block[i][b] for i in letters) <= 1

    return model, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
