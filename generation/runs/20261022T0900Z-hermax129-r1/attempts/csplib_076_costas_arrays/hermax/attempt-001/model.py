from hermax.model import Model


def build(instance):
    # Costas Array: find permutation where all pairwise differences are unique.
    n = instance["n"]

    m = Model()

    # costas[i] = position of mark in row i (1-based indexing, values 1..n)
    costas = m.int_vector("costas", n, 1, n)

    # All positions must be different (permutation constraint)
    m &= costas.all_different()

    # All pairwise differences must be unique
    # For each distance l from 1 to n-1:
    #   For each starting position i from 0 to n-l-1:
    #     The difference costas[i+l] - costas[i] must be unique across all (l, i) pairs

    # Collect all difference variables
    all_diffs = []

    for l in range(1, n):
        for i in range(n - l):
            diff = costas[i + l] - costas[i]
            all_diffs.append(diff)

    # All differences must be different
    # We create auxiliary variables to capture the differences
    diff_vars = []
    for l in range(1, n):
        for i in range(n - l):
            diff_var = m.int(f"diff_l{l}_i{i}", -(n - 1), n - 1)
            m &= (diff_var == costas[i + l] - costas[i])
            diff_vars.append(diff_var)

    # All differences must be all_different
    m &= diff_vars.all_different()

    return m, {"costas": costas}
