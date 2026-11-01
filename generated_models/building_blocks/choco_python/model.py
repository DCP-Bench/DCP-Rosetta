# building_blocks: a Choco-solver (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python building_blocks.py building_blocks.json

from pychoco.model import Model


def create_model(instance):
    """Alphabet blocks have a letter on each side, and together carry every letter of the
    alphabet used. Arranged in various ways they must spell all the words of a given list;
    find which letters sit on which block."""
    n_blocks = instance["num_blocks"]      # the number of blocks
    n_sides = instance["num_sides"]        # the number of sides of a block, one letter each
    n_letters = instance["num_letters"]    # the number of letters spread over the blocks
    alphabet = instance["alphabet"]        # the letters, in order; letter i is alphabet[i]
    words_str = instance["words_str"]      # the words that must be spelled

    # words[w] is the word w as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    model = Model()

    # dice[i] is the block that carries letter i
    dice = [model.intvar(0, n_blocks - 1, name=f"dice_{i}") for i in range(n_letters)]

    # The letters of a word sit on different blocks, since a block shows one letter at a time.
    for word in words:
        model.all_different([dice[letter] for letter in word]).post()

    # Each block carries exactly n_sides letters.
    model.global_cardinality(dice, list(range(n_blocks)),
                             [model.intvar(n_sides, n_sides) for _ in range(n_blocks)]).post()

    return model, {"dice": dice}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
