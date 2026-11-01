# building_blocks: a CPMpy model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python building_blocks.py building_blocks.json

import cpmpy as cp


def create_model(instance):
    """Alphabet blocks have a letter on each side, and together carry every letter of the
    alphabet used. Arranged in various ways they must spell all the words of a given list;
    find which letters sit on which block."""
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    num_letters = instance["num_letters"]  # the number of letters spread over the blocks
    alphabet = instance["alphabet"]        # the letters, in order; letter i is alphabet[i]
    words_str = instance["words_str"]      # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    # dice[i] is the block (0 to num_blocks - 1) that carries letter i
    dice = cp.intvar(0, num_blocks - 1, shape=num_letters, name="dice")

    model = cp.Model()
    # A word can be spelled only if its letters come from different blocks.
    for word in words:
        model.add(cp.AllDifferent(dice[word]))
    # Every block carries exactly num_sides letters.
    for block in range(num_blocks):
        model.add(cp.sum(dice == block) == num_sides)

    return model, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
