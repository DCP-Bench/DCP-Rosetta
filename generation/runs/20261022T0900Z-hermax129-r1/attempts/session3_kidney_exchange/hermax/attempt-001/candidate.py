from hermax.model import Model


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]  # 1-based: people that i can donate to

    m = Model()
    give = m.bool_matrix("give", n, n)

    # Only compatible pairs can be transplanted; nobody donates to themselves.
    allowed = [set(j - 1 for j in compatible[i]) for i in range(n)]
    for i in range(n):
        for j in range(n):
            if j not in allowed[i]:
                m &= ~give[i][j]

    # Anyone who gives a kidney must receive one: a person's donations
    # and receipts are equal, and each person gives at most one and
    # receives at most one kidney.
    for i in range(n):
        out_i = sum(give[i][j] for j in range(n))
        in_i = sum(give[j][i] for j in range(n))
        m &= (out_i == in_i)
        m &= (out_i <= 1)
        m &= (in_i <= 1)

    # Maximise the number of people who receive a kidney: every transplant
    # gives exactly one receiver, so maximise the number of transplants.
    total = sum(give[i][j] for i in range(n) for j in range(n))
    m.obj += 0 - total

    return m, {"transplants": give}
