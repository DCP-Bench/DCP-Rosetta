# building_blocks: a Z3 (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python building_blocks.py building_blocks.json

import z3


def create_model(instance):
    """Alphabet blocks have a letter on each side, and together carry every letter of the
    alphabet used. Arranged in various ways they must spell all the words of a given list;
    find which letters sit on which block."""
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    num_letters = instance["num_letters"]  # the number of letters spread over the blocks
    alphabet = instance["alphabet"]        # the letters used on the blocks, in order
    words_str = instance["words_str"]      # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    # dice[i] is the block that carries letter i of the alphabet
    dice = [z3.Int(f"dice_{i}") for i in range(num_letters)]

    solver = z3.Solver()

    # Each letter sits on one of the blocks.
    solver.add([z3.And(d >= 0, d <= num_blocks - 1) for d in dice])

    # A word can be spelled only if its letters come from different blocks.
    solver.add([z3.Distinct([dice[i] for i in word]) for word in words])

    # Every block carries exactly num_sides letters.
    solver.add([z3.Sum([z3.If(d == block, 1, 0) for d in dice]) == num_sides
                for block in range(num_blocks)])

    return solver, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
