from hermax.model import Model


def build(instance):
    """
    Magic sequence problem: find a sequence x of length n such that for all i,
    the number i occurs exactly x[i] times in the sequence.

    Example: [6, 2, 1, 0, 0, 0, 1, 0, 0, 0] means:
    - 0 appears 6 times, 1 appears 2 times, 2 appears 1 time, 3-9 appear 0 times

    Instance: n - the length of the sequence
    Output: x - the magic sequence
    """
    n = instance["n"]

    m = Model()

    # x[i] is the count of how many times i appears in the sequence
    # x[i] is between 0 and n
    x = m.int_vector("x", n, 0, n)

    # Constraint 1: the sum of x[i] must equal n (total elements)
    m &= (sum(x) == n)

    # Constraint 2: for each i, the number of occurrences of i equals x[i]
    # This is the core magic sequence constraint
    for i in range(n):
        # Create boolean variables for whether each position equals i
        is_i = m.bool_vector(f"is_{i}", n)
        for j in range(n):
            # is_i[j] is true when x[j] == i
            m &= (is_i[j] == (x[j] == i))
        # Sum of is_i equals x[i]
        count_i = m.sum_var(is_i)
        m &= (count_i == x[i])

    return m, {"x": x}
