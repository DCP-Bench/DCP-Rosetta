# csplib_016_traffic_lights: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from docplex.mp.model import Model


def create_model(instance):
    """Traffic lights: four crossings in a ring, each with a vehicle light V_i (r, ry, g, y as
    0..3) and a pedestrian light P_i (r, g as 0..1). Neighbouring crossings i and i+1 (with
    crossing 5 being crossing 1) must show one of the allowed combinations (V_i, P_i, V_i+1, P_i+1)."""
    allowed = instance["allowed_tuples"]  # allowed (V_i, P_i, V_i+1, P_i+1) combinations
    crossings = 4  # the problem has four crossings in a ring

    model = Model("traffic_lights")

    # vehicle[i] is the state of light V(i + 1): 0 red, 1 red-yellow, 2 green, 3 yellow;
    # pedestrian[i] is the state of light P(i + 1): 0 red, 1 green
    vehicle = [model.integer_var(0, 3, name=f"V{i + 1}") for i in range(crossings)]
    pedestrian = [model.integer_var(0, 1, name=f"P{i + 1}") for i in range(crossings)]

    # Every pair of neighbouring crossings i and i + 1 (crossing 4 is next to crossing 1) shows
    # one allowed combination. shows[t] is 1 when the pair shows the t-th allowed combination;
    # exactly one is shown, and the pair's four lights take its values.
    for i in range(crossings):
        nxt = (i + 1) % crossings
        shows = model.binary_var_list(len(allowed), name=f"shows_{i}")
        model.add_constraint(model.sum(shows) == 1)
        model.add_constraint(vehicle[i] == model.scal_prod(shows, [t[0] for t in allowed]))
        model.add_constraint(pedestrian[i] == model.scal_prod(shows, [t[1] for t in allowed]))
        model.add_constraint(vehicle[nxt] == model.scal_prod(shows, [t[2] for t in allowed]))
        model.add_constraint(pedestrian[nxt] == model.scal_prod(shows, [t[3] for t in allowed]))

    return model, {"lights": vehicle + pedestrian}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
