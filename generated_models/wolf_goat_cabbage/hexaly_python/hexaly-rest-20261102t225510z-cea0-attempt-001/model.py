"""Wolf, goat and cabbage: cross the river in the given number of stages without anything being eaten."""
import hexaly.optimizer as hx


def build(instance):
    stages = instance["stage"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Position of each at every stage: 0 = starting shore, 1 = destination shore
    boat_pos = [model.bool() for _ in range(stages)]
    items = {name: [model.bool() for _ in range(stages)] for name in ("wolf", "goat", "cabbage")}

    # Everything starts on the starting shore and ends on the destination shore
    model.constraint(boat_pos[0] == 0)
    model.constraint(boat_pos[stages - 1] == 1)
    for positions in items.values():
        model.constraint(positions[0] == 0)
        model.constraint(positions[stages - 1] == 1)

    for t in range(stages - 1):
        # The boat crosses the river at every step
        model.constraint(boat_pos[t + 1] != boat_pos[t])
        # The farmer carries at most one item, which must be on the boat's shore; the rest stay
        moved = []
        for positions in items.values():
            changes = positions[t + 1] != positions[t]
            model.constraint(model.or_(model.not_(changes), positions[t] == boat_pos[t]))
            moved.append(changes)
        model.constraint(model.sum(moved) <= 1)

    for t in range(stages):
        # Left unattended (on the shore the boat is not at), the wolf would eat the goat, the goat the cabbage
        for hunter, prey in (("wolf", "goat"), ("goat", "cabbage")):
            together = items[hunter][t] == items[prey][t]
            model.constraint(model.or_(model.not_(together), items[hunter][t] == boat_pos[t]))

    return optimizer, {"wolf_pos": items["wolf"], "goat_pos": items["goat"],
                       "cabbage_pos": items["cabbage"], "boat_pos": boat_pos}
