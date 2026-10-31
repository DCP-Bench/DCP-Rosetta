from hermax.model import Model


def build(instance):
    init = instance["init"]
    n_coins = len(init)
    n_moves = instance["num_moves"]

    m = Model()

    # state[t][i] is True for tails and False for heads, for coin i after
    # t moves. Row 0 is the start and row n_moves the end.
    state = m.bool_matrix("state", n_moves + 1, n_coins)

    # The start is the given arrangement (1 means tails).
    for i in range(n_coins):
        m &= (state[0][i] if init[i] == 1 else ~state[0][i])

    # Each move flips exactly one coin.
    for t in range(n_moves):
        # changed[i] is True when coin i differs between move t and t + 1
        # (an exclusive or, written as four clauses).
        changed = m.bool_vector(f"changed_{t}", n_coins)
        for i in range(n_coins):
            a = state[t][i]
            b = state[t + 1][i]
            c = changed[i]
            m &= (~c | a | b)
            m &= (~c | ~a | ~b)
            m &= (c | ~a | b)
            m &= (c | a | ~b)
        m &= changed.exactly_one()

    # The final arrangement is all heads or all tails: all coins agree.
    last = state[n_moves]
    for i in range(n_coins - 1):
        m &= (last[i] | ~last[i + 1])
        m &= (~last[i] | last[i + 1])

    return m, {"steps": state}
