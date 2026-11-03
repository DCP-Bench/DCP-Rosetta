"""Word design: num_words DNA words of length n with 4 C/G symbols, pairwise distance and reverse-complement conditions."""
import hexaly.optimizer as hx


def build(instance):
    n, num_words = instance["n"], instance["num_words"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # words[w][k] is the letter at position k of word w: 1 = A, 2 = C, 3 = G, 4 = T
    words = [[model.int(1, 4) for _ in range(n)] for _ in range(num_words)]

    # Each word has 4 symbols from {C, G}, letters 2 and 3
    for w in range(num_words):
        model.constraint(model.sum(model.and_(letter >= 2, letter <= 3) for letter in words[w]) == 4)
    # Each pair of distinct words differs in at least 4 positions
    for a in range(num_words):
        for b in range(a + 1, num_words):
            model.constraint(model.sum(words[a][k] != words[b][k] for k in range(n)) >= 4)
    # For every pair (x, y), x identical to y included, the reverse of x and the Watson-Crick
    # complement of y differ in at least 4 positions. The complement swaps A/T and C/G, which
    # maps letter v to 5 - v, so position k differs when x[n-1-k] != 5 - y[k].
    for a in range(num_words):
        for b in range(num_words):
            model.constraint(model.sum(words[a][n - 1 - k] + words[b][k] != 5 for k in range(n)) >= 4)

    return optimizer, {"words": words}
