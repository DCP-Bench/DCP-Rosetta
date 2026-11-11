# building_blocks: a CPLEX (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python building_blocks.py building_blocks.json

from docplex.mp.model import Model


def create_model(instance):
    """Building blocks: put the letters on the blocks, a fixed number per block, so that every word can be spelled with distinct blocks."""
    num_blocks = instance["num_blocks"]  # number of blocks
    num_sides = instance["num_sides"]    # number of sides, hence of letters, of each block
    alphabet = instance["alphabet"]      # the letters; letter number i is alphabet[i]
    letters = range(instance["num_letters"])
    blocks = range(num_blocks)
    position = {letter: i for i, letter in enumerate(alphabet)}
    # instance["words_str"]: the words to spell; each is turned into the numbers of its letters
    words = [[position[c] for c in word] for word in instance["words_str"]]

    model = Model("building_blocks")

    # on[letter, b] is 1 when the letter is on block b.
    on = model.binary_var_matrix(letters, blocks, name="on")

    # Each letter is on exactly one block.
    model.add_constraints(model.sum(on[letter, b] for b in blocks) == 1 for letter in letters)

    # The letters of a word are on different blocks, so no block carries two of them. A word
    # that repeats a letter cannot be spelled: that letter is on one block only.
    model.add_constraints(model.sum(on[letter, b] for letter in word) <= 1
                          for word in words for b in blocks)

    # Every block has num_sides letters, one on each side.
    model.add_constraints(model.sum(on[letter, b] for letter in letters) == num_sides for b in blocks)

    # dice[letter] is the block, 0 .. num_blocks - 1, that the letter is on.
    dice = [model.sum(b * on[letter, b] for b in blocks) for letter in letters]

    return model, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
