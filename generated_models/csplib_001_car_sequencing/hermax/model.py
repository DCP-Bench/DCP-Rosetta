# csplib_001_car_sequencing: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from hermax.model import Model


def create_model(instance):
    """Car sequencing: put the cars of a production line in one order so that every car
    type is built as many times as it is ordered, each position holds exactly one car,
    and no assembly station is asked to fit more than its capacity into any run of
    consecutive cars."""
    demand = instance["demand"]        # demand[c]: how many cars of type c are ordered
    requires = instance["requires"]    # requires[c][o]: 1 when a car of type c needs option o
    at_most = instance["at_most"]      # at_most[o]: the most cars needing option o allowed in a window
    per_slots = instance["per_slots"]  # per_slots[o]: the window length, in consecutive cars, for option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)  # one position in the sequence per car

    m = Model()

    # x[p][c] is true when the car at position p of the line is of type c
    x = m.bool_matrix("x", n_cars, n_types)

    # Every position of the line holds exactly one car type.
    for p in range(n_cars):
        m &= x.row(p).exactly_one()

    # Each car type appears exactly as often as it is ordered.
    for c in range(n_types):
        m &= (sum(x[p][c] for p in range(n_cars)) == demand[c])

    # needs[o][p] is true when the car at position p needs option o, i.e. its type requires it.
    # A Boolean per position and option keeps each window constraint short (a measured speed-up:
    # it solves the largest instance in a fraction of the time of one sum over every car-type pair).
    needs = []
    for o in range(n_options):
        needing = [c for c in range(n_types) if requires[c][o]]
        row = []
        for p in range(n_cars):
            nb = m.bool()
            if needing:
                m &= (sum(x[p][c] for c in needing) >= 1).iff(nb)
            else:
                m &= ~nb  # no type needs this option, so no car at any position does
            row.append(nb)
        needs.append(row)

    # Each station: in every window of per_slots[o] consecutive cars, at most at_most[o]
    # cars may need option o.
    for o in range(n_options):
        window = per_slots[o]
        for start in range(n_cars - window + 1):
            m &= (sum(needs[o][p] for p in range(start, start + window)) <= at_most[o])

    # The output: the car type at each position, as the number of its type.
    sequence = [sum(c * x[p][c] for c in range(n_types)) for p in range(n_cars)]
    return m, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
