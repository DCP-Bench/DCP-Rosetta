from hermax.model import Model


def build(instance):
    m = Model()
    # statements[k - 1] is true when statement k holds.
    statements = m.bool_vector("statement", 5)

    # Statement k says "exactly k of these statements are false", which is
    # the same as exactly 5 - k of them being true. Each statement is
    # reified to its own count condition.
    for k in range(1, 6):
        m &= (sum(statements) == 5 - k).iff(statements[k - 1])

    return m, {"statements": statements}
