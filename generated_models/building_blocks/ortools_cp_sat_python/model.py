# building_blocks: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install ortools`):
#   python building_blocks.py building_blocks.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Alphabet blocks have a letter on each side, and together carry every letter of the
    alphabet used. Arranged in various ways they must spell all the words of a given list;
    find which letters sit on which block."""
    n_blocks = instance["num_blocks"]    # the number of blocks
    n_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    n_letters = instance["num_letters"]  # the number of letters spread over the blocks
    alphabet = instance["alphabet"]      # the letters used on the blocks
    words_str = instance["words_str"]    # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    model = cp_model.CpModel()

    # dice[i] is the block that carries letter i
    dice = [model.new_int_var(0, n_blocks - 1, f"dice_{i}") for i in range(n_letters)]
    # on_block[i][b] is true when letter i is on block b
    on_block = [[model.new_bool_var(f"on_block_{i}_{b}") for b in range(n_blocks)]
                for i in range(n_letters)]
    # Letter i is on block b exactly when dice[i] is b.
    for i in range(n_letters):
        for b in range(n_blocks):
            model.add(dice[i] == b).only_enforce_if(on_block[i][b])
            model.add(dice[i] != b).only_enforce_if(~on_block[i][b])

    # A word can be spelled only if its letters come from different blocks.
    for word in words:
        model.add_all_different([dice[letter] for letter in word])

    # Every block carries one letter per side.
    for b in range(n_blocks):
        model.add(sum(on_block[i][b] for i in range(n_letters)) == n_sides)

    return model, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
