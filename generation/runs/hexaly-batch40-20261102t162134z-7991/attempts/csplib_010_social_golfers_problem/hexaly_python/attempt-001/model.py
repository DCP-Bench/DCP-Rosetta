"""Social golfers: schedule groups for several weeks so that no two golfers play together more than once."""
import hexaly.optimizer as hx


def build(instance):
    weeks, groups, size = instance["n_weeks"], instance["n_groups"], instance["group_size"]
    golfers = groups * size
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # assign[i][w] is the group (0-based) of golfer i in week w
    assign = [[model.int(0, groups - 1) for _ in range(weeks)] for _ in range(golfers)]

    # Every group of every week has exactly group_size golfers
    for w in range(weeks):
        for g in range(groups):
            model.constraint(model.sum(assign[i][w] == g for i in range(golfers)) == size)
    # No two golfers share a group in more than one week
    for i in range(golfers):
        for j in range(i + 1, golfers):
            model.constraint(model.sum(assign[i][w] == assign[j][w] for w in range(weeks)) <= 1)

    return optimizer, {"assign": assign}
