"""Bus scheduling: buses start in 4-hour slots and run 8 hours; cover each slot's demand with the fewest buses."""
import hexaly.optimizer as hx


def build(instance):
    # demands[i] = number of buses needed in the i-th 4-hour interval of the day (6 intervals)
    demands = instance["demands"]
    n = len(demands)  # number of 4-hour intervals in the day
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] = number of buses that start their 8-hour shift in interval i.
    # Upper bound (derived): max(demands) buses starting in one interval already cover any
    # single interval's demand, so an optimum never needs more.
    x = [model.int(0, max(demands)) for _ in range(n)]

    # The number of buses available in each interval meets its demand. A bus runs two successive
    # intervals, the day wrapping around: interval i + 1 is served by the buses that started in
    # interval i and those starting in interval i + 1
    for i in range(n):
        model.constraint(x[i] + x[(i + 1) % n] >= demands[(i + 1) % n])

    # Minimise the number of buses
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
