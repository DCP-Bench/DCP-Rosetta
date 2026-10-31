from hermax.model import Model


def build(instance):
    graph = instance["graph"]
    n = len(graph)

    m = Model()

    # celebrities[i] is True if person i is a celebrity
    celebrities = m.bool_vector("celebrities", n)

    # Constraint 1: A celebrity is known by everyone (all people know them)
    # If person i is a celebrity, then graph[j][i] = 1 for all j
    for i in range(n):
        for j in range(n):
            if graph[j][i] == 0:
                # If graph[j][i] = 0, then person i cannot be a celebrity
                m &= ~celebrities[i]

    # Constraint 2: A celebrity only knows other celebrities (and themselves)
    # If person i is a celebrity and graph[i][j] = 1, then person j must also be a celebrity
    for i in range(n):
        for j in range(n):
            if i != j and graph[i][j] == 1:
                # If person i is a celebrity and knows person j, then j must be a celebrity
                m &= (celebrities[i] <= celebrities[j])
            # If person i is a celebrity and graph[i][j] = 0 (for j != i),
            # then j must not be a non-celebrity that i knows
            # This is already covered by the previous constraint

    # Constraint 3: At least one celebrity exists
    m &= celebrities.at_least_one()

    return m, {"celebrities": celebrities}
