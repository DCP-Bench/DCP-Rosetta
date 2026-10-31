from hermax.model import Model


def build(instance):
    """Schedule 4 people into 4 interview slots based on their free-busy schedules.

    Input m[i][j] = 1 if person i is free in slot j, 0 if busy.
    Output x[i][j] = True if person i is assigned to slot j.

    Constraints:
    - Each person assigned to exactly one slot (exactly_one per row)
    - Each slot gets exactly one person (exactly_one per column)
    - Person can only be assigned to a slot where they're free
    """
    m = instance["m"]

    model = Model()
    x = model.bool_matrix("x", 4, 4)

    # Each person is assigned to exactly one slot
    for i in range(4):
        model &= x.row(i).exactly_one()

    # Each slot gets exactly one person
    for j in range(4):
        model &= x.col(j).exactly_one()

    # A person can only be assigned to a slot where they're free
    # If m[i][j] = 0 (busy), then x[i][j] must be False
    for i in range(4):
        for j in range(4):
            if m[i][j] == 0:
                model &= ~x[i][j]

    return model, {"x": x}
