from hermax.model import Model


def build(instance):
    sets = instance["sets"]
    k = instance["num_correct_digits"]
    n = len(sets[0])

    m = Model()
    # The account number holds each digit from 0 to n-1 exactly once.
    x = m.int_vector("x", n, 0, n - 1)
    m &= x.all_different()

    # In each set, exactly k digits are in their correct position.
    for s in sets:
        m &= (sum(x[i] == s[i] for i in range(n)) == k)

    return m, {"x": x}
