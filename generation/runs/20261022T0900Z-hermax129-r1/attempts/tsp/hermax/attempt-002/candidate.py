import math

from hermax.model import Model


def build(instance):
    locations = instance["locations"]
    n = len(locations)

    # Distance: Euclidean distance between the points, rounded to an integer.
    dist = [
        [
            int(round(math.sqrt((locations[i][0] - locations[j][0]) ** 2
                                + (locations[i][1] - locations[j][1]) ** 2)))
            for j in range(n)
        ]
        for i in range(n)
    ]

    m = Model()

    # at[i][k]: city i is visited at place k of the tour. A permutation of the cities.
    at = m.bool_matrix("at", n, n)
    # go[i][j]: city j is visited directly after city i (cyclically).
    go = m.bool_matrix("go", n, n)

    # Each city has exactly one place, and each place holds exactly one city.
    for i in range(n):
        m &= at.row(i).exactly_one()
    for k in range(n):
        m &= at.col(k).exactly_one()

    # Each city is left once and entered once ("visits each city exactly once").
    for i in range(n):
        m &= go.row(i).exactly_one()
    for j in range(n):
        m &= go.col(j).exactly_one()

    # Tie go to at, in both directions: go[i][j] is the successor relation of the tour
    # ("returns to the origin city": place n-1 wraps to place 0).
    for i in range(n):
        for j in range(n):
            for k in range(n):
                k1 = (k + 1) % n
                m &= (~at[i][k] | ~at[j][k1] | go[i][j])
                m &= (~go[i][j] | ~at[i][k] | at[j][k1])

    # Start the tour at city 0 (fixes the rotation).
    m &= at[0][0]

    # Symmetric distances: city 1 comes before city 2 in the tour (fixes the reflection).
    for k in range(n):
        lits = [~at[2][k]] + [at[1][kk] for kk in range(k)]
        clause = lits[0]
        for lit in lits[1:]:
            clause = clause | lit
        m &= clause

    # Travel distance: sum of the rounded Euclidean distances of the legs taken.
    length = sum(dist[i][j] * go[i][j] for i in range(n) for j in range(n) if i != j and dist[i][j] != 0)
    m.obj += length

    return m, {"travel_distance": length}
