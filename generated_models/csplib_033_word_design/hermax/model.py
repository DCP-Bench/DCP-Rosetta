# csplib_033_word_design: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_033_word_design.py csplib_033_word_design.json

from hermax.model import Model

# Constants fixed by the problem statement, not instance fields.
A, C, G, T = 1, 2, 3, 4  # letters are coded 1..4
CG_PER_WORD = 4          # each word has exactly this many letters from {C, G}
MIN_DISTANCE = 4         # the required number of differing positions


def create_model(instance):
    """Find a set of num_words words of length n over the alphabet {A, C, G, T}, where
    each word has exactly four letters from {C, G}, any two distinct words differ in at
    least four positions, and for every pair x, y of words (x and y may be the same word)
    the reverse of x and the Watson-Crick complement of y differ in at least four positions."""
    n = instance["n"]                  # n: the length of each word
    num_words = instance["num_words"]  # num_words: how many words the set must contain

    m = Model()

    # words[i][j] is letter j of word i, coded 1..4 as A, C, G, T
    words = m.int_matrix("words", num_words, n, A, T)

    # complement[i][j] is the Watson-Crick complement of words[i][j]: A<->T and C<->G.
    # With this coding A + T = 5 and C + G = 5, so the complement is 5 - letter.
    complement = m.int_matrix("complement", num_words, n, A, T)
    for i in range(num_words):
        for j in range(n):
            m &= (complement[i][j] + words[i][j] == A + T)

    # strong[i][j] is true when letter j of word i is C or G (codes 2 and 3)
    strong = m.bool_matrix("strong", num_words, n)
    for i in range(num_words):
        for j in range(n):
            m &= m.table([words[i][j], strong[i][j]],
                         allowed=[(A, False), (C, True), (G, True), (T, False)])

    # Each word has exactly four letters from {C, G}.
    for i in range(num_words):
        m &= (sum(strong[i][j] for j in range(n)) == CG_PER_WORD)

    # Two distinct words differ in at least four positions. differs[j] may be true
    # only where the letters at position j are different; the count of true ones is
    # then a lower bound on the real distance, which is all the requirement needs.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            differs = m.bool_vector(f"differs_{x}_{y}", n)  # differs[j]: words x and y differ at j
            for j in range(n):
                m &= (words[x][j] != words[y][j]).only_if(differs[j])
            m &= (sum(differs[j] for j in range(n)) >= MIN_DISTANCE)

    # The reverse of word x and the complement of word y differ in at least four
    # positions, for every pair x, y (x = y included). Substituting
    # j -> n-1-j and complementing both sides turns the (y, x) condition into the
    # (x, y) one, so only the pairs x <= y are posted.
    for x in range(num_words):
        for y in range(x, num_words):
            # rev_differs[j]: position j of reversed x (letter n-1-j of x) differs from
            # the complement of y at position j
            rev_differs = m.bool_vector(f"rev_differs_{x}_{y}", n)
            for j in range(n):
                m &= (words[x][n - 1 - j] != complement[y][j]).only_if(rev_differs[j])
            m &= (sum(rev_differs[j] for j in range(n)) >= MIN_DISTANCE)

    # No objective: any set of words meeting the requirements is an answer.
    return m, {"words": words}


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
