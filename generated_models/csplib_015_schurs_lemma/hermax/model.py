from hermax.model import Model


def build(instance):
    # Schur's Lemma: partition n balls into c boxes such that
    # for any triple (x, y, z) with x + y = z, not all three are in the same box.

    n = instance["n"]  # Number of balls (1 to n)
    c = instance["c"]  # Number of boxes

    m = Model()

    # balls[i] is the box (1 to c) that ball i+1 is in
    balls = m.int_vector("balls", n, 1, c)

    # Constraint: for each x + y = z where 1 <= x <= y < z <= n,
    # not all three balls can be in the same box.
    # This means: for each such triple and each box j,
    # at least one of x, y, z must NOT be in box j.
    # Equivalently: sum(balls[i] == j for i in {x-1, y-1, z-1}) <= 2

    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z <= n:
                # For each box, at most 2 of {x, y, z} can be in it
                for box in range(1, c + 1):
                    count = m.sum_var([
                        (balls[x-1] == box),
                        (balls[y-1] == box),
                        (balls[z-1] == box)
                    ])
                    m &= (count <= 2)

    return m, {"balls": balls}
