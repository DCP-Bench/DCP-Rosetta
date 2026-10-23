from hermax.model import Model

# Letters: 1 = A, 2 = C, 3 = G, 4 = T. Fixed constants of the problem:
# C and G are 2 and 3; the Watson-Crick complement maps v to 5 - v (A<->T, C<->G).


def build(instance):
    n = instance["n"]                  # word length
    W = instance["num_words"]          # number of words in the set

    m = Model()
    words = m.int_matrix("words", W, n, 1, 4)

    # Each word has exactly four symbols from {C, G}.
    for w in range(W):
        gc = []
        for i in range(n):
            x = words[w][i]
            g = m.bool()
            m &= (~g | (x >= 2))
            m &= (~g | (x <= 3))
            m &= (g | (x <= 1) | (x >= 4))
            gc.append(g)
        m &= (sum(gc) == 4)

    # Distinct words differ in at least 4 positions.
    for a in range(W):
        for b in range(a + 1, W):
            differ = []
            for i in range(n):
                e = m.bool()
                m &= (words[a][i] == words[b][i]).iff(e)
                differ.append(~e)
            m &= (sum(differ) >= 4)

    # For every ordered pair (x, y), including x = y: reverse(x) and complement(y) differ in at least 4 positions.
    # Position i of reverse(x) is x[n-1-i]; position i of complement(y) is 5 - y[i].
    # They agree exactly when x[n-1-i] + y[i] == 5.
    for a in range(W):
        for b in range(W):
            agree = []
            for i in range(n):
                f = m.bool()
                m &= (words[a][n - 1 - i] + words[b][i] == 5).iff(f)
                agree.append(f)
            m &= (sum(agree) <= n - 4)

    return m, {"words": words}
