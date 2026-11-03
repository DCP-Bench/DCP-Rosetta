# building_blocks: a hermax (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install hermax`):
#   python building_blocks.py building_blocks.json

from hermax.model import Model


def create_model(instance):
    """Alphabet blocks each carry one letter on every side, and together the blocks
    carry every letter of the alphabet. Decide which block carries each letter so
    that every word in the list can be spelled, which needs its letters to sit on
    different blocks. Satisfaction problem: any valid arrangement will do."""
    alphabet = instance["alphabet"]        # the letters, in the order they are numbered
    num_blocks = instance["num_blocks"]    # how many blocks there are
    num_sides = instance["num_sides"]      # how many letters each block carries
    num_letters = instance["num_letters"]  # how many letters are placed, one dice entry each
    words_str = instance["words_str"]      # the words that must be spelled

    # Each word as the list of its letters' numbers in `alphabet`.
    letter_index = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_index[c] for c in word] for word in words_str]

    m = Model()
    # dice[l] is the block (numbered from 0) that carries letter number l
    dice = m.int_vector("dice", num_letters, 0, num_blocks - 1)

    # The letters of each word sit on different blocks, so the word can be spelled.
    for word in words:
        m &= m.vector([dice[letter] for letter in word]).all_different()

    # Every block carries exactly num_sides letters.
    for block in range(num_blocks):
        m &= (sum((dice[letter] == block) for letter in range(num_letters)) == num_sides)

    return m, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
