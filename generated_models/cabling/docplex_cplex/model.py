# cabling: a CPLEX (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python cabling.py cabling.json

from docplex.mp.model import Model


def create_model(instance):
    """Cabling: place devices in a rack, one per position, so that the total cable length is as
    short as possible. Some pairs of devices are joined by several cables, and a cable is as long
    as the distance between the positions of its two devices."""
    n = instance["n"]                      # number of devices, and of rack positions
    devices = instance["devices"]          # names of the devices
    cable_struct = instance["cable_struct"]  # rows [device, device, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    # cables[k] is (first device, second device, number of cables between them), devices as numbers
    cables = [(index[a], index[b], count) for a, b, count in cable_struct]

    model = Model("cabling")

    # at[d, p] is 1 when device d sits in rack position p.
    at = model.binary_var_matrix(range(n), range(n), name="at")

    # Every device has exactly one position and every position holds exactly one device
    # (all devices have distinct positions).
    model.add_constraints(model.sum(at[d, p] for p in range(n)) == 1 for d in range(n))
    model.add_constraints(model.sum(at[d, p] for d in range(n)) == 1 for p in range(n))

    # position[d] is the rack position of device d.
    position = [model.sum(p * at[d, p] for p in range(n)) for d in range(n)]

    # length[k] is the length of one cable of the k-th pair: the distance between the two
    # positions. It is bounded below by both differences. Only the lengths' sum is
    # minimized and every number of cables is positive, so the minimum takes each length down
    # to the larger of the two differences, which is the distance.
    length = [model.integer_var(0, n - 1, name=f"length_{k}") for k in range(len(cables))]
    for k, (a, b, count) in enumerate(cables):
        model.add_constraint(length[k] >= position[a] - position[b])
        model.add_constraint(length[k] >= position[b] - position[a])

    # The sum of all cable lengths: each pair's distance times its number of cables.
    final_sum = model.sum(count * length[k] for k, (_, _, count) in enumerate(cables))

    # Objective: minimize the total cable length.
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
