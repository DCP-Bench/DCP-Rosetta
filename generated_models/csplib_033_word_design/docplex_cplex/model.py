# csplib_033_word_design: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_033_word_design.py csplib_033_word_design.json

from itertools import combinations
from docplex.mp.model import Model


def create_model(instance):
    """Word design: find num_words words of length n over the letters A, C, G, T such that each word
    has exactly 4 letters from {C, G}, any two different words differ in at least 4 positions, and
    for any two words x and y (possibly the same word) the reverse of x and the Watson-Crick
    complement of y differ in at least 4 positions."""
    LETTERS = (1, 2, 3, 4)  # the letters A, C, G, T, coded 1, 2, 3, 4: a fixed part of the problem
    STRONG = (2, 3)         # the letters C and G
    MIN_DISTANCE = 4        # positions in which two words must differ: a fixed part of the problem
    STRONG_PER_WORD = 4     # letters from {C, G} in every word: a fixed part of the problem
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words in the set

    positions = range(n)
    words = range(num_words)

    model = Model("word_design")
    # The distance rules below are quadratic constraints over binaries, which are not
    # convex. CPLEX refuses such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # letter[x, j, c] is 1 when the j-th letter of word x is c.
    letter = model.binary_var_cube(words, positions, LETTERS, name="letter")

    # Every position of every word holds exactly one letter.
    model.add_constraints(model.sum(letter[x, j, c] for c in LETTERS) == 1
                          for x in words for j in positions)

    # Each word has exactly 4 letters from {C, G}.
    model.add_constraints(
        model.sum(letter[x, j, c] for j in positions for c in STRONG) == STRONG_PER_WORD
        for x in words)

    # Two different words differ in at least 4 positions, i.e. they agree in at most n - 4.
    # The agreements are counted as products of the two words' letter indicators.
    for x, y in combinations(words, 2):
        agreements = model.sum(letter[x, j, c] * letter[y, j, c]
                               for j in positions for c in LETTERS)
        model.add_constraint(agreements <= n - MIN_DISTANCE)

    # For every pair of words x and y (also x with itself), the reverse of x and the
    # complement of y differ in at least 4 positions. Position j compares the letter of x at
    # n - 1 - j with the complement of the letter of y at j; the complement of c is 5 - c.
    # The pair (y, x) gives the same rule as (x, y), so each unordered pair is stated once.
    for x in words:
        for y in range(x, num_words):
            agreements = model.sum(letter[x, n - 1 - j, c] * letter[y, j, 5 - c]
                                   for j in positions for c in LETTERS)
            model.add_constraint(agreements <= n - MIN_DISTANCE)

    # words[x][j] is the letter (1 for A, 2 for C, 3 for G, 4 for T) at position j of word x.
    return model, {"words": [[model.sum(c * letter[x, j, c] for c in LETTERS) for j in positions]
                             for x in words]}


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
