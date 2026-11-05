"""Car sequencing: order the cars on the assembly line so that no option station is over capacity in any window.
Each car type needs some of the options; the station for option o copes with at most at_most[o] cars in any
per_slots[o] consecutive cars."""
import hexaly.optimizer as hx


def build(instance):
    # at_most[o], per_slots[o]: the station for option o handles at most at_most[o] cars out of any per_slots[o]
    # consecutive cars on the line (a capacity of at_most[o] / per_slots[o])
    at_most, per_slots = instance["at_most"], instance["per_slots"]
    # demand[c] = number of cars of type c to produce; requires[c][o] = 1 if a car of type c needs option o
    demand, requires = instance["demand"], instance["requires"]
    n_types, n_options = len(demand), len(at_most)  # number of car types, number of options (stations)
    n = sum(demand)  # one slot per car to produce
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_type[t][c] = 1 if the car in slot t is of type c. Booleans with linear sums keep the
    # model linear, the form Hexaly proves bounds on.
    is_type = [[model.bool() for _ in range(n_types)] for _ in range(n)]

    # Every slot holds exactly one car
    for t in range(n):
        model.constraint(model.sum(is_type[t]) == 1)
    # Exactly demand[c] cars of type c are produced
    for c in range(n_types):
        model.constraint(model.sum(is_type[t][c] for t in range(n)) == demand[c])

    # needs[t][o] = 1 if the car in slot t requires option o (the sum picks the types that require o)
    needs = [[model.sum(is_type[t][c] for c in range(n_types) if requires[c][o]) for o in range(n_options)]
             for t in range(n)]
    # Station o copes with at most at_most[o] cars in any per_slots[o] consecutive slots. Windows start at slots
    # 0 .. n - per_slots[o]; a window longer than the line becomes a single window over all slots.
    for o in range(n_options):
        window = per_slots[o]
        for start in range(max(1, n - window + 1)):
            model.constraint(model.sum(needs[t][o] for t in range(start, min(n, start + window))) <= at_most[o])

    # sequence[t] = type of the car in slot t, numbered from 0 (the output of the problem)
    sequence = [model.sum(c * is_type[t][c] for c in range(n_types)) for t in range(n)]
    return optimizer, {"sequence": sequence}
