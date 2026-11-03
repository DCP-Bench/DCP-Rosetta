"""Car sequencing: order the cars on the assembly line so that no option station is over capacity in any window."""
import hexaly.optimizer as hx


def build(instance):
    at_most, per_slots = instance["at_most"], instance["per_slots"]
    demand, requires = instance["demand"], instance["requires"]
    n_types, n_options = len(demand), len(at_most)
    n = sum(demand)  # one slot per car to produce
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_type[t][c] = 1 if the car in slot t is of type c. Booleans with linear sums keep the
    # model linear, which gives Hexaly bounds that integer types compared with == do not.
    is_type = [[model.bool() for _ in range(n_types)] for _ in range(n)]

    # Every slot holds exactly one car
    for t in range(n):
        model.constraint(model.sum(is_type[t]) == 1)
    # Exactly demand[c] cars of type c are produced
    for c in range(n_types):
        model.constraint(model.sum(is_type[t][c] for t in range(n)) == demand[c])

    # needs[t][o] = 1 if the car in slot t requires option o
    needs = [[model.sum(is_type[t][c] for c in range(n_types) if requires[c][o]) for o in range(n_options)]
             for t in range(n)]
    # Station o copes with at most at_most[o] cars in any per_slots[o] consecutive slots
    for o in range(n_options):
        window = per_slots[o]
        for start in range(max(1, n - window + 1)):
            model.constraint(model.sum(needs[t][o] for t in range(start, min(n, start + window))) <= at_most[o])

    # The car type in each slot, numbered from 0
    sequence = [model.sum(c * is_type[t][c] for c in range(n_types)) for t in range(n)]
    return optimizer, {"sequence": sequence}
