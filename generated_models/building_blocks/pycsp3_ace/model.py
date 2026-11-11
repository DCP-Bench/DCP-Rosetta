# building_blocks: a PyCSP3 model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python building_blocks.py building_blocks.json

from pycsp3 import *


def create_model(instance):
    """Alphabet blocks, each with one letter on each of its sides, carry every letter but Q
    and Z. Each letter is on exactly one block, and every block has the same number of sides.
    Place the letters so that every given word can be spelled: its letters lie on different
    blocks, each block being used for at most one letter of the word. Find the block of every
    letter."""
    alphabet = instance["alphabet"]        # the letters to place; alphabet[i] is letter i
    num_letters = instance["num_letters"]  # the number of letters, one per side of all blocks
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides, hence letters, on each block
    words = instance["words_str"]          # the words that must be spellable

    # dice[i] is the block that letter alphabet[i] is placed on
    dice = VarArray(size=num_letters, dom=range(num_blocks))

    satisfy(
        # Every block has the same number of sides, so each block carries num_sides letters.
        Cardinality(dice, occurrences={block: num_sides for block in range(num_blocks)}),
        # Each word can be spelled: its letters lie on different blocks.
        [AllDifferent(dice[alphabet.index(letter)] for letter in word) for word in words],
    )

    return {"dice": dice}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
