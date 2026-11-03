# csplib_033_word_design: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

import cvc5.pythonic as c5


def create_model(instance):
    """Find num_words words of length n over the letters A, C, G and T such that each word has
    four letters from C and G, any two different words differ in at least four positions, and
    the reverse of any word x differs from the Watson-Crick complement of any word y in at least
    four positions (x and y may be the same word)."""
    n = instance["n"]                  # the length of each word
    num_words = instance["num_words"]  # the number of words in the set

    letters = ["A", "C", "G", "T"]  # the four letters of the alphabet
    cg = (1, 2)                     # the positions of C and G in letters

    # is_letter[i][k][v] is true when word i has letter v at position k
    is_letter = [[[c5.Bool(f"is_letter_{i}_{k}_{v}") for v in range(len(letters))]
                  for k in range(n)]
                 for i in range(num_words)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    def same_letter(a, b):
        """True when the letter flags a and b pick the same letter."""
        return c5.Or([c5.And(x, y) for x, y in zip(a, b)])

    # Each position of each word holds exactly one letter.
    for i in range(num_words):
        for k in range(n):
            solver.add(c5.Sum([c5.If(f, 1, 0) for f in is_letter[i][k]]) == 1)

    # Each word has four letters from C and G.
    for i in range(num_words):
        solver.add(
            c5.Sum([c5.If(is_letter[i][k][v], 1, 0) for k in range(n) for v in cg]) == 4)

    # Two different words differ in at least four positions.
    for i in range(num_words):
        for j in range(i + 1, num_words):
            # same[k] is true when the two words have the same letter at position k
            same = [same_letter(is_letter[i][k], is_letter[j][k]) for k in range(n)]
            solver.add(c5.Sum([c5.If(c5.Not(s), 1, 0) for s in same]) >= 4)

    # The reverse of word x differs from the Watson-Crick complement of word y in at least four
    # positions, for every pair x, y, including x = y. The complement swaps A with T and C with G,
    # which is the reversed list of letter flags.
    for i in range(num_words):
        for j in range(num_words):
            # agree[k] is true when x, read backwards, and the complement of y agree at position k
            agree = [same_letter(is_letter[i][n - 1 - k], is_letter[j][k][::-1]) for k in range(n)]
            solver.add(c5.Sum([c5.If(c5.Not(a), 1, 0) for a in agree]) >= 4)

    # Each letter as its number: A is 1, C is 2, G is 3, T is 4.
    words = [[c5.Sum([c5.If(is_letter[i][k][v], v + 1, 0) for v in range(len(letters))])
              for k in range(n)]
             for i in range(num_words)]

    return solver, {"words": words}


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
