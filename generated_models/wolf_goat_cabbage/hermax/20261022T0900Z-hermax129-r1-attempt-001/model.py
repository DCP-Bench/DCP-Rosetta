from hermax.model import Model


def build(instance):
    stages = instance["stage"]     # number of positions in the plan, 0..stages-1

    m = Model()
    # Each position is 0 for the starting shore and 1 for the destination shore.
    wolf = m.bool_vector("wolf", stages)
    goat = m.bool_vector("goat", stages)
    cabbage = m.bool_vector("cabbage", stages)
    boat = m.bool_vector("boat", stages)

    # Everything starts on the starting shore.
    m &= ~wolf[0]
    m &= ~goat[0]
    m &= ~cabbage[0]
    m &= ~boat[0]

    # Everything ends on the destination shore.
    last = stages - 1
    m &= wolf[last]
    m &= goat[last]
    m &= cabbage[last]
    m &= boat[last]

    for t in range(stages):
        # Safety: the wolf must not be left with the goat, and the goat not
        # with the cabbage, unless the farmer is on the same shore.
        # Clause for v = 1: wolf and goat both on shore 1, boat on shore 0 is
        # forbidden. Clause for v = 0: the mirror case.
        m &= (~wolf[t]) | (~goat[t]) | boat[t]
        m &= wolf[t] | goat[t] | (~boat[t])
        m &= (~goat[t]) | (~cabbage[t]) | boat[t]
        m &= goat[t] | cabbage[t] | (~boat[t])

    for t in range(stages - 1):
        # The farmer crosses the river at every stage, so the boat changes shore.
        m &= boat[t] | boat[t + 1]
        m &= (~boat[t]) | (~boat[t + 1])

        # An item moves only when the boat moves with it, so it must be on the
        # shore the boat leaves: a forbidden move is an item that changes shore
        # while sitting on the other shore from the boat.
        m &= wolf[t] | (~wolf[t + 1]) | (~boat[t])
        m &= (~wolf[t]) | wolf[t + 1] | boat[t]
        m &= goat[t] | (~goat[t + 1]) | (~boat[t])
        m &= (~goat[t]) | goat[t + 1] | boat[t]
        m &= cabbage[t] | (~cabbage[t + 1]) | (~boat[t])
        m &= (~cabbage[t]) | cabbage[t + 1] | boat[t]

        # The boat carries the farmer and at most one item: at most one item
        # changes shore in each crossing.
        moved_wolf = m.bool()
        moved_goat = m.bool()
        moved_cabbage = m.bool()
        m &= (wolf[t] + wolf[t + 1] == 1).iff(moved_wolf)
        m &= (goat[t] + goat[t + 1] == 1).iff(moved_goat)
        m &= (cabbage[t] + cabbage[t + 1] == 1).iff(moved_cabbage)
        m &= (moved_wolf + moved_goat + moved_cabbage <= 1)

    return m, {
        "wolf_pos": wolf,
        "goat_pos": goat,
        "cabbage_pos": cabbage,
        "boat_pos": boat,
    }
