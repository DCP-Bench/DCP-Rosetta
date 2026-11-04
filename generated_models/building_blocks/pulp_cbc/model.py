# building_blocks: a PuLP (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python building_blocks.py building_blocks.json

import pulp


def create_model(instance):
    """Alphabet blocks have a letter on each side, and together carry every letter of the
    alphabet used. Arranged in various ways they must spell all the words of a given list;
    find which letters sit on which block."""
    n_blocks = instance["num_blocks"]    # the number of blocks
    n_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    n_letters = instance["num_letters"]  # the number of letters spread over the blocks
    alphabet = instance["alphabet"]      # the letters, in order; letter i is alphabet[i]
    words_str = instance["words_str"]    # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    problem = pulp.LpProblem("building_blocks", pulp.LpMinimize)

    # on[i][b] is 1 when letter i is on block b, and 0 when not.
    on = [[pulp.LpVariable(f"on_{i}_{b}", cat="Binary") for b in range(n_blocks)]
          for i in range(n_letters)]
    # dice[i] is the block that carries letter i, numbered from 0.
    dice = [pulp.LpVariable(f"dice_{i}", 0, n_blocks - 1, cat="Integer")
            for i in range(n_letters)]

    for i in range(n_letters):
        # Each letter sits on exactly one block.
        problem += pulp.lpSum(on[i]) == 1
        # The number of a letter's block is the block it sits on.
        problem += dice[i] == pulp.lpSum(b * on[i][b] for b in range(n_blocks))

    # Every block carries exactly n_sides letters.
    for b in range(n_blocks):
        problem += pulp.lpSum(on[i][b] for i in range(n_letters)) == n_sides

    # The letters of a word lie on different blocks, so a block holds at most one of them.
    for word in words:
        for b in range(n_blocks):
            problem += pulp.lpSum(on[letter][b] for letter in word) <= 1

    return problem, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
