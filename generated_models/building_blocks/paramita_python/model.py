# building_blocks: a Paramita (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python building_blocks.py building_blocks.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Alphabet blocks have one letter on each side, and together they carry every letter
    of the alphabet. Turning the blocks in turn must spell every word of the list; find the
    block that carries each letter."""
    alphabet = instance["alphabet"]      # the letters on the blocks, in alphabetical order
    n_blocks = instance["num_blocks"]    # the number of blocks
    n_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    n_letters = instance["num_letters"]  # the number of letters on the blocks
    words = instance["words_str"]        # the words that must be spelled

    # y[l][b] is true when letter l is on block b
    y = [[Bool(f"y_{l}_{b}") for b in range(n_blocks)] for l in range(n_letters)]
    # all constraints of the model
    cons = []

    # Each letter is on exactly one block.
    cons += [sum(y[l]) == 1 for l in range(n_letters)]

    # Each block shows n_sides letters.
    cons += [sum(y[l][b] for l in range(n_letters)) == n_sides for b in range(n_blocks)]

    # The letters of a word sit on different blocks, so turning the blocks in turn can show it.
    for word in words:
        # positions in the alphabet of the distinct letters of the word
        word_letters = sorted({alphabet.index(ch) for ch in word})
        cons += [sum(y[l][b] for l in word_letters) <= 1 for b in range(n_blocks)]

    # dice[l] is the block that carries letter l.
    dice = [sum(b * y[l][b] for b in range(n_blocks)) for l in range(n_letters)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
