from hermax.model import Model


def build(instance):
    size = instance["size"]

    m = Model()

    # marks[i] is the position of the i-th mark
    # marks[0] = 0 (first mark at 0)
    # marks are in strictly increasing order
    # Upper bound: for a Golomb ruler of size n, optimal length grows roughly as n^2
    # Use a reasonable upper bound based on size
    max_length = size * size
    marks = m.int_vector("marks", size, 0, max_length)

    # First mark is always 0
    m &= (marks[0] == 0)

    # Marks are in strictly increasing order
    for i in range(size - 1):
        m &= (marks[i] < marks[i + 1])

    # All pairwise differences must be distinct
    # For a Golomb ruler, all differences a_j - a_i (i < j) must be distinct
    # Create difference variables and constrain them to computed differences
    diff_count = size * (size - 1) // 2
    diff_vars = m.int_vector("diffs", diff_count, 0, max_length)

    # Constrain the difference variables to equal the computed differences
    idx = 0
    for i in range(size):
        for j in range(i + 1, size):
            m &= (diff_vars[idx] == marks[j] - marks[i])
            idx += 1

    # All differences must be distinct
    m &= diff_vars.all_different()

    # Objective: minimize the length (the last mark position)
    length = marks[size - 1]
    m.obj += length

    return m, {"marks": marks, "length": length}
