import math

from hermax.model import Model


def build(instance):
    points = instance["locations"]
    n = len(points)

    # Distance between two points: Euclidean, rounded to the nearest integer.
    def dist(i, j):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        return int(math.floor(math.hypot(dx, dy) + 0.5))

    m = Model()

    # x[i][j] is True when the tour goes directly from city i to city j.
    x = m.bool_matrix("x", n, n)

    # No city is followed by itself.
    for i in range(n):
        m &= ~x[i][i]

    # Each city is left exactly once and entered exactly once.
    for i in range(n):
        m &= x.row(i).exactly_one()
        m &= x.col(i).exactly_one()

    # Subtour elimination (Miller-Tucker-Zemlin). pos[i] is the position of
    # city i on the tour, with city 0 at position 0. Every move from city i to
    # city j (both not the start) must go to a later position.
    pos = m.int_vector("pos", n, 0, n - 1)
    m &= (pos[0] == 0)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                m &= (pos[j] >= pos[i] + 1).only_if(x[i][j])

    # Direction symmetry: a tour and its reverse have the same length. Keep
    # the one whose successor of city 0 has a smaller index than its
    # predecessor: forbid successor j with predecessor k when j > k.
    for j in range(1, n):
        for k in range(1, n):
            if j > k:
                m &= (~x[0][j] | ~x[k][0])

    # Total travel distance over the chosen moves, minimised.
    total = sum(dist(i, j) * x[i][j] for i in range(n) for j in range(n) if i != j)
    m.obj += total

    return m, {"travel_distance": total}
