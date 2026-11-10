# csplib_033_word_design: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_033_word_design.py csplib_033_word_design.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf

A, C, G, T = 0, 1, 2, 3  # the four letters
LETTERS = (A, C, G, T)


def create_model(instance):
    """Find num_words words of length n over the letters A, C, G and T such that every word has
    four letters from C and G, any two different words differ in at least four positions, and the
    reverse of any word x differs from the Watson-Crick complement of any word y (x and y may be
    the same word) in at least four positions."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set

    # letter[w][p][l] is true when word w has letter l at position p
    letter = [[{l: Bool(f"letter_{w}_{p}_{l}") for l in LETTERS} for p in range(n)]
              for w in range(num_words)]

    # The constraints of the model, collected as they are added.
    constraints = []

    # Two words, given position by position as letter flags, differ in at least four positions.
    # d[p] can be true only where the two letters at position p are different.
    def differ_in_four(tag, first, second):
        d = [Bool(f"d_{tag}_{p}") for p in range(n)]
        for p in range(n):
            for l in LETTERS:
                constraints.append(If(d[p], ~(first[p][l] & second[p][l])))
        constraints.append(sum(d) >= 4)

    # Every position of every word holds exactly one letter.
    for w in range(num_words):
        for p in range(n):
            constraints.append(sum(letter[w][p][l] for l in LETTERS) == 1)

    # Each word has exactly four letters from C and G.
    for w in range(num_words):
        constraints.append(sum(letter[w][p][C] + letter[w][p][G] for p in range(n)) == 4)

    # Distinct words differ in at least four positions. Each unordered pair is checked once.
    for w1 in range(num_words):
        for w2 in range(w1 + 1, num_words):
            differ_in_four(f"ham_{w1}_{w2}", letter[w1], letter[w2])

    # The reverse of word x and the Watson-Crick complement of word y differ in at least four
    # positions, for every ordered pair (x, y), including x = y. The complement pairs A with T and
    # C with G, so letter l of y becomes letter 3 - l.
    for w1 in range(num_words):
        for w2 in range(num_words):
            reverse_first = [letter[w1][n - 1 - p] for p in range(n)]
            complement_second = [{l: letter[w2][p][3 - l] for l in LETTERS} for p in range(n)]
            differ_in_four(f"rc_{w1}_{w2}", reverse_first, complement_second)

    # Each word as letter codes: 1 for A, 2 for C, 3 for G, 4 for T.
    words = [[sum((l + 1) * letter[w][p][l] for l in LETTERS) for p in range(n)]
             for w in range(num_words)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"words": words}


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
