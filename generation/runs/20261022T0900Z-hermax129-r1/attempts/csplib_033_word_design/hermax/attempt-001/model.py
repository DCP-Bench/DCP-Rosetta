from hermax.model import Model


def build(instance):
    """
    Word design problem (DNA): find num_words strings of length n over {A,C,G,T}
    where A=1, C=2, G=3, T=4, with constraints:
    - Each word has exactly 4 symbols from {C, G} (values 2 or 3)
    - Each pair of distinct words differ in at least 4 positions
    - For each pair of words x and y: reverse(x) and complement(y) differ in at least 4 positions
      (complement: A<->T, C<->G)

    Instance: n (word length), num_words (number of words)
    Output: words - matrix of num_words x n integers
    """
    n = instance["n"]
    num_words = instance["num_words"]

    m = Model()

    # words[i][j] is the symbol at position j in word i (1-4 representing A,C,G,T)
    words = m.int_matrix("words", num_words, n, 1, 4)

    # Constraint 1: Each word has exactly 4 C's or G's (values 2 or 3)
    for i in range(num_words):
        cg_count = m.int("cg_" + str(i), 0, n)
        m &= (cg_count == sum_cg_symbols(m, words.row(i), n))
        m &= (cg_count == 4)

    # Constraint 2: Each pair of distinct words differ in at least 4 positions
    for i in range(num_words):
        for j in range(i + 1, num_words):
            diff_count = m.int("diff_" + str(i) + "_" + str(j), 0, n)
            m &= (diff_count == sum_diffs(m, words.row(i), words.row(j), n))
            m &= (diff_count >= 4)

    # Constraint 3: For each pair (x, y): reverse(x) and complement(y) differ in at least 4 positions
    for i in range(num_words):
        for j in range(num_words):
            rev_comp_diff = m.int("rev_comp_diff_" + str(i) + "_" + str(j), 0, n)
            m &= (rev_comp_diff == sum_rev_comp_diffs(m, words.row(i), words.row(j), n))
            m &= (rev_comp_diff >= 4)

    return m, {"words": words}


def sum_cg_symbols(m, word_row, n):
    """Count C's and G's in a word"""
    is_cg = m.bool_vector("is_cg", n)
    for j in range(n):
        # is_cg[j] is true if word_row[j] is 2 (C) or 3 (G)
        m &= (is_cg[j] == ((word_row[j] == 2) | (word_row[j] == 3)))
    return m.sum_var(is_cg)


def sum_diffs(m, word1, word2, n):
    """Count positions where two words differ"""
    diffs = m.bool_vector("diff", n)
    for j in range(n):
        # diffs[j] is true iff word1[j] != word2[j]
        m &= diffs[j].implies(word1[j] != word2[j])
        m &= (~diffs[j]).implies(word1[j] == word2[j])
    return m.sum_var(diffs)


def sum_rev_comp_diffs(m, word_x, word_y, n):
    """Count positions where reverse(x) and complement(y) differ"""
    diffs = m.bool_vector("rev_comp", n)
    for j in range(n):
        # reverse(x)[j] = x[n-1-j]
        x_rev_j = word_x[n - 1 - j]
        # complement(y)[j] = transform(y[j])
        # A(1) <-> T(4), C(2) <-> G(3)
        y_comp_j_val = m.int("y_comp_" + str(j), 1, 4)
        # If y[j] == 1 (A), then complement is 4 (T)
        # If y[j] == 2 (C), then complement is 3 (G)
        # If y[j] == 3 (G), then complement is 2 (C)
        # If y[j] == 4 (T), then complement is 1 (A)
        m &= ((word_y[j] == 1).implies(y_comp_j_val == 4))
        m &= ((word_y[j] == 2).implies(y_comp_j_val == 3))
        m &= ((word_y[j] == 3).implies(y_comp_j_val == 2))
        m &= ((word_y[j] == 4).implies(y_comp_j_val == 1))

        # diffs[j] is true iff x_rev_j != y_comp_j_val
        m &= diffs[j].implies(x_rev_j != y_comp_j_val)
        m &= (~diffs[j]).implies(x_rev_j == y_comp_j_val)
    return m.sum_var(diffs)
