"""Chess set: how many small and large boxwood chess sets to make each week to maximise profit."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Numbers of small and large sets per week; 160 lathe-hours and 200 kg of boxwood bound them
    small_set = model.int(0, 160)
    large_set = model.int(0, 160)

    # Lathe hours: 3 per small set and 2 per large set, 160 available (four lathes, 40 hours each)
    model.constraint(3 * small_set + 2 * large_set <= 160)
    # Boxwood: 1 kg per small set and 3 kg per large set, 200 kg available
    model.constraint(small_set + 3 * large_set <= 200)

    # Profit: $5 per small set and $20 per large set
    max_profit = 5 * small_set + 20 * large_set
    model.maximize(max_profit)
    return optimizer, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}
