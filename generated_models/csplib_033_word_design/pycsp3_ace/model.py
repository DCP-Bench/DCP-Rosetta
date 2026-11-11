# csplib_033_word_design: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_033_word_design.py csplib_033_word_design.json

from pycsp3 import *


def create_model(instance):
    """Find a set of words of length n over the alphabet A, C, G, T such that each word has
    4 symbols from {C, G}, each pair of distinct words differ in at least 4 positions, and for
    each pair of words x and y (which may be identical) the reverse of x and the Watson-Crick
    complement of y differ in at least 4 positions. Letters are coded 1 = A, 2 = C, 3 = G, 4 = T."""
    n = instance["n"]                    # the length of each word
    num_words = instance["num_words"]    # the number of words in the set

    cg_codes = [2, 3]                    # the codes of C and G
    n_cg = 4                             # each word has exactly 4 symbols from {C, G}
    min_distance = 4                     # the minimum number of positions in which two words differ
    complement_sum = 5                   # code(A) + code(T) = code(C) + code(G) = 5, so the complement of code v is 5 - v

    # words[i][j] is the letter at position j of word i
    words = VarArray(size=[num_words, n], dom={1, 2, 3, 4})

    satisfy(
        # Each word has n_cg symbols from {C, G}.
        [Count(words[i], values=cg_codes) == n_cg for i in range(num_words)],
        # Each pair of distinct words differs in at least min_distance positions.
        [Hamming(words[i], words[j]) >= min_distance for i in range(num_words) for j in range(i + 1, num_words)],
        # For every pair of words x and y, possibly identical, the reverse of x and the complement of y
        # differ in at least min_distance positions.
        [
            Sum(words[i][n - 1 - k] != complement_sum - words[j][k] for k in range(n)) >= min_distance
            for i in range(num_words)
            for j in range(num_words)
        ],
    )

    return {"words": words}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("words", "=")
        for row in outputs["words"]:
            print(values(row))
    else:
        print("No solution:", status())
