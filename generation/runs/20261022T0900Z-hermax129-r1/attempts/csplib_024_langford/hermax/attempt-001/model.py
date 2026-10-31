from hermax.model import Model


def build(instance):
    # Langford pairing of order k: place two copies of each value v in 1..k in a sequence
    # of length 2k so that the copies of v are separated by exactly v numbers
    # (their positions differ by v + 1).
    k = instance["k"]
    length = 2 * k

    m = Model()

    sol = m.int_vector("sol", length, 1, k)

    # start[v][a]: the first copy of value v sits at position a, the second at a + v + 1.
    start = {}
    for v in range(1, k + 1):
        width = length - 1 - v  # positions a with a + v + 1 <= length - 1
        start[v] = m.bool_vector(f"start_{v}", width)
        m &= start[v].exactly_one()

    # Each position holds exactly one number: the copies of v cover positions a and a + v + 1.
    for p in range(length):
        covering = []
        for v in range(1, k + 1):
            width = length - 1 - v
            # The copy at position p comes from a start at p (first copy) or at p - v - 1 (second copy).
            if p < width:
                covering.append(start[v][p])
            if 0 <= p - v - 1 < width:
                covering.append(start[v][p - v - 1])
        m &= (sum(covering) == 1)

    # The number at a position is the value whose copy occupies it.
    for v in range(1, k + 1):
        width = length - 1 - v
        for a in range(width):
            m &= (~start[v][a] | (sol[a] == v))
            m &= (~start[v][a] | (sol[a + v + 1] == v))

    return m, {"sol": sol}
