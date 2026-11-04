# csplib_013_progressive_party_problem: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    # the boats
    boats = range(n_boats)
    # the half-hour periods
    periods = range(n_periods)

    model = cp_model.CpModel()

    # is_host[b] is true when boat b is a host boat
    is_host = [model.new_bool_var(f"is_host_{b}") for b in boats]
    # visits[p][b] is the boat that the crew of boat b is on in period p (b itself for a host)
    visits = [[model.new_int_var(0, n_boats - 1, f"visits_{p}_{b}") for b in boats] for p in periods]
    # at[p][b][h] is true when the crew of boat b is on boat h in period p
    at = [[[model.new_bool_var(f"at_{p}_{b}_{h}") for h in boats] for b in boats] for p in periods]
    # Each crew is on exactly one boat in each period, and visits reports which one.
    for p in periods:
        for b in boats:
            model.add_exactly_one(at[p][b])
            model.add(visits[p][b] == sum(h * at[p][b][h] for h in boats))

    # The crew of a host boat stays on its own boat in every period.
    for b in boats:
        for p in periods:
            model.add(visits[p][b] == b).only_enforce_if(is_host[b])

    # The people aboard a boat in a period, host crew included, do not outnumber its capacity.
    for p in periods:
        for h in boats:
            model.add(sum(crew_size[b] * at[p][b][h] for b in boats) <= capacity[h])

    for b in boats:
        # A guest crew never visits the same host twice.
        for h in boats:
            model.add(sum(at[p][b][h] for p in periods) <= 1).only_enforce_if(~is_host[b])
        # A boat that is not a host is never visited.
        for p in periods:
            for c in boats:
                model.add(at[p][c][b] == 0).only_enforce_if(~is_host[b])

    # Two crews are on the same boat in at most one period.
    for c1 in boats:
        for c2 in range(c1 + 1, n_boats):
            # together[p] is true when crews c1 and c2 are on the same boat in period p
            together = []
            for p in periods:
                same = model.new_bool_var(f"together_{p}_{c1}_{c2}")
                model.add(visits[p][c1] == visits[p][c2]).only_enforce_if(same)
                model.add(visits[p][c1] != visits[p][c2]).only_enforce_if(~same)
                together.append(same)
            model.add(sum(together) <= 1)

    # Minimise the number of host boats.
    model.minimize(sum(is_host))

    return model, {"visits": visits, "is_host": is_host}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
