# building_blocks: an Exact (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python building_blocks.py building_blocks.json

from exact import Exact


def create_model(instance):
    """Each alphabet block has one letter on each of its sides. Together the blocks carry every
    letter used. Arranged in various ways, they must spell all the words of a list; find which
    letters sit on which block."""
    n_blocks = instance["num_blocks"]    # the number of blocks
    n_sides = instance["num_sides"]      # the number of sides on a block, one letter each
    n_letters = instance["num_letters"]  # the number of letters the blocks carry
    alphabet = instance["alphabet"]      # the letters the blocks carry
    words_str = instance["words_str"]    # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    solver = Exact()

    # Exact identifies its variables by name.
    # dice[l] is the block that carries letter l
    dice = [f"dice_{l}" for l in range(n_letters)]
    # on_block[l][b] is 1 when letter l is on block b, and 0 when not
    on_block = [[f"on_block_{l}_{b}" for b in range(n_blocks)] for l in range(n_letters)]
    for l in range(n_letters):
        solver.addVariable(dice[l], 0, n_blocks - 1)
        for name in on_block[l]:
            solver.addVariable(name, 0, 1)
        # Each letter is on exactly one block.
        solver.addConstraint([(1, name) for name in on_block[l]], True, 1, True, 1)
        # dice[l] matches the block that letter l sits on.
        solver.addConstraint([(b, on_block[l][b]) for b in range(1, n_blocks)] + [(-1, dice[l])],
                             True, 0, True, 0)

    # The letters of each word sit on different blocks.
    for word in words:
        for b in range(n_blocks):
            solver.addConstraint([(1, on_block[l][b]) for l in word], False, 0, True, 1)

    # Each block carries exactly n_sides letters.
    for b in range(n_blocks):
        solver.addConstraint([(1, on_block[l][b]) for l in range(n_letters)],
                             True, n_sides, True, n_sides)

    return solver, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
