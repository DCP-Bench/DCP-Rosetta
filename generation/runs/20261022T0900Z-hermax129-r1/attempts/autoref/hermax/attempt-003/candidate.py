from hermax.model import Model


def build(instance):
    # Sizes come from the instance: n + 2 entries, indexed 0 .. n + 1.
    n = instance["n"]
    m_val = instance["m"]
    length = n + 2

    # Every entry of S is a value in 0 .. n, so every entry is counted by
    # one of the self-describing constraints below. Without this bound,
    # entries above n escape the counts and the model has extra solutions.
    model = Model()
    s = model.int_vector("s", length, 0, n)

    # Last entry is m.
    model &= (s[n + 1] == m_val)

    # Self-describing: for each value i in 0 .. n, the number of entries
    # equal to i is s[i]. Counting is the sum of Boolean literals (s[j] == i).
    for i in range(n + 1):
        count_i = model.sum_var([(s[j] == i) for j in range(length)])
        model &= (count_i == s[i])

    return model, {"s": s}
