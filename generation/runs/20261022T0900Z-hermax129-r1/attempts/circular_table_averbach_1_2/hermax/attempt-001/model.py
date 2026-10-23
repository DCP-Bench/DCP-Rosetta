from hermax.model import Model


def build(instance):
    # Three players: X, Y, Z seated around a circular table at positions 0, 1, 2
    # Three nationalities: American, English, French at positions 0, 1, 2

    # Create model and variables
    m = Model()
    # Each person is assigned to a position (0, 1, or 2)
    x = m.int("x", 0, 2)
    y = m.int("y", 0, 2)
    z = m.int("z", 0, 2)

    # Each nationality is assigned to a position (0, 1, or 2)
    american = m.int("american", 0, 2)
    english = m.int("english", 0, 2)
    french = m.int("french", 0, 2)

    # Constraint: X, Y, Z are all different (permutation of positions)
    people_vector = m.int_vector("people", 3, 0, 2)
    m &= people_vector.all_different()
    m &= (people_vector[0] == x)
    m &= (people_vector[1] == y)
    m &= (people_vector[2] == z)

    # Constraint: American, English, French are all different (permutation of positions)
    nations_vector = m.int_vector("nations", 3, 0, 2)
    m &= nations_vector.all_different()
    m &= (nations_vector[0] == american)
    m &= (nations_vector[1] == english)
    m &= (nations_vector[2] == french)

    # Constraint 1: Y passed three hearts to the American
    # Y passes cards to the right, so american == (y + 1) % 3
    # Express as three disjunctive clauses (implications)
    # NOT(y == 0) OR (american == 1) means: if y == 0 then american == 1
    # NOT(y == 1) OR (american == 2) means: if y == 1 then american == 2
    # NOT(y == 2) OR (american == 0) means: if y == 2 then american == 0
    m &= ~(y == 0) | (american == 1)
    m &= ~(y == 1) | (american == 2)
    m &= ~(y == 2) | (american == 0)

    # Constraint 2: X passed cards to the person who passed cards to the Frenchwoman
    # french == (x + 2) % 3
    # NOT(x == 0) OR (french == 2) means: if x == 0 then french == 2
    # NOT(x == 1) OR (french == 0) means: if x == 1 then french == 0
    # NOT(x == 2) OR (french == 1) means: if x == 2 then french == 1
    m &= ~(x == 0) | (french == 2)
    m &= ~(x == 1) | (french == 0)
    m &= ~(x == 2) | (french == 1)

    return m, {
        "x": x,
        "y": y,
        "z": z,
        "american": american,
        "english": english,
        "french": french
    }
