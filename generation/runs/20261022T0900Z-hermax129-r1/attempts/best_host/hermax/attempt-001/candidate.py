from hermax.model import Model


def build(instance):
    # Dinner table seating arrangement problem.
    # 6 guests must be seated around a circular table.
    # Each guest can only sit next to specific other guests.

    # Guests: 0=Andrew, 1=Betty, 2=Cara, 3=Dave, 4=Erica, 5=Frank

    # Allowed edges: pairs that CAN sit next to each other
    allowed_edges = {
        (0, 3), (3, 0),  # Andrew - Dave (bidirectional)
        (0, 5), (5, 0),  # Andrew - Frank
        (1, 2), (2, 1),  # Betty - Cara
        (1, 4), (4, 1),  # Betty - Erica
        (2, 5), (5, 2),  # Cara - Frank
        (3, 4), (4, 3),  # Dave - Erica
    }

    m = Model()

    # x is a permutation of [0, 1, 2, 3, 4, 5]
    x = m.int_vector("x", 6, 0, 5)
    m &= x.all_different()

    # Adjacency constraints: for circular seating, forbid disallowed edges.
    # For each position i, the edge (x[i], x[i+1]) must be allowed.
    # We express this by forbidding all disallowed edges.
    for i in range(6):
        current = x[i]
        next_pos = x[(i + 1) % 6]

        # For each disallowed edge (a, b), add constraint that forbids it
        for a in range(6):
            for b in range(6):
                if a != b and (a, b) not in allowed_edges:
                    # Forbid this edge: NOT (current == a AND next == b)
                    # Which is: (current != a) OR (next != b)
                    m &= (current != a) | (next_pos != b)

    return m, {"x": x}
