from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    # x[p] is the card at circle position p (0-based); the cards are 1..n.
    x = m.int_vector("x", n, 1, n)
    m &= x.all_different()
    # Rotating the circle gives another valid arrangement, so fix card 1 at
    # position 0 to pick one representative per rotation.
    m &= (x[0] == 1)

    # Jump target of each position: position p + card, wrapping clockwise.
    # wrap[p] is 1 exactly when p + card runs past the last position, so
    # nxt[p] = p + x[p] - n * wrap[p] stays in 0..n-1.
    nxt = m.int_vector("nxt", n, 0, n - 1)
    wrap = m.bool_vector("wrap", n)
    for p in range(n):
        m &= (nxt[p] == p + x[p] - n * wrap[p])

    # The frog starts on card 1 and visits positions v[0], v[1], ... in turn.
    # Covering all n cards means the first n visited positions are distinct.
    s = m.int("start", 0, n - 1)
    m &= (x[s] == 1)
    v = m.int_vector("v", n, 0, n - 1)
    m &= (v[0] == s)
    for t in range(n - 1):
        m &= (nxt[v[t]] == v[t + 1])
    m &= v.all_different()

    return m, {"x": x}
