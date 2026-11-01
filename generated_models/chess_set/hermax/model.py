from hermax.model import Model


def build(instance):
    # Problem parameters (fixed constraints from problem description)
    # Small set: 3 hours lathe, 1 kg wood, $5 profit
    # Large set: 2 hours lathe, 3 kg wood, $20 profit
    # Resources: 160 lathe-hours, 200 kg wood
    lathe_hours_total = 160
    wood_total = 200
    small_lathe_hours = 3
    large_lathe_hours = 2
    small_wood = 1
    large_wood = 3
    small_profit = 5
    large_profit = 20

    # Create model and variables
    m = Model()
    # Upper bounds: at most 200 kg wood for large sets (if all large), or 160 lathe-hours (if all large)
    # Max small sets: 200 / 1 = 200 (wood constraint) or 160 / 3 = 53 (lathe constraint)
    # Max large sets: 200 / 3 = 66 (wood constraint) or 160 / 2 = 80 (lathe constraint)
    small_set = m.int("small_set", 0, 66)
    large_set = m.int("large_set", 0, 80)

    # Resource constraints
    # Lathe-hours: 3 * small_set + 2 * large_set <= 160
    m &= (3 * small_set + 2 * large_set <= lathe_hours_total)

    # Wood: 1 * small_set + 3 * large_set <= 200
    m &= (small_set + 3 * large_set <= wood_total)

    # Objective: maximize profit = 5 * small_set + 20 * large_set
    # In MaxSAT, we minimize, so we minimize the negative of profit
    total_profit = 5 * small_set + 20 * large_set
    m.obj += -total_profit

    return m, {
        "small_set": small_set,
        "large_set": large_set,
        "max_profit": total_profit
    }
