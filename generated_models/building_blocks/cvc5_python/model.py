# building_blocks: a cvc5 (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python building_blocks.py building_blocks.json

import cvc5.pythonic as c5


def create_model(instance):
    """Alphabet blocks with one letter on each side must be arranged so that every word in
    a list can be spelled, with the letters of each word on different blocks. Find the
    block that carries each letter."""
    alphabet = instance["alphabet"]        # the letters on the blocks; alphabet[i] is letter i
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides on each block
    num_letters = instance["num_letters"]  # the number of letters on the blocks
    words = instance["words_str"]          # the words that must be spelled

    # dice[i] is the block that carries alphabet[i]
    dice = [c5.Int(f"dice_{i}") for i in range(num_letters)]

    solver = c5.Solver()

    # Each letter sits on one of the blocks.
    for i in range(num_letters):
        solver.add(dice[i] >= 0)
        solver.add(dice[i] <= num_blocks - 1)

    # Each block carries num_sides letters.
    for b in range(num_blocks):
        solver.add(c5.Sum([c5.If(dice[i] == b, 1, 0) for i in range(num_letters)]) == num_sides)

    # The letters of a word sit on different blocks.
    for word in words:
        letters = [dice[alphabet.index(c)] for c in word]
        if len(letters) > 1:
            solver.add(c5.Distinct(letters))

    return solver, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
