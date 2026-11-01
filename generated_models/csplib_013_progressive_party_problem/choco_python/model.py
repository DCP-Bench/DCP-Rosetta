# csplib_013_progressive_party_problem: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from pychoco.model import Model


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts, and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    model = Model()

    # is_host[b] is true when boat b is a host boat
    is_host = [model.boolvar(name=f"is_host_{b}") for b in range(n_boats)]
    # visits[p][b] is the boat that the crew of boat b is on in period p (b itself for a host)
    visits = [[model.intvar(0, n_boats - 1, name=f"visits_{p}_{b}") for b in range(n_boats)]
              for p in range(n_periods)]
    # at[p][b][h] is true when the crew of boat b is on boat h in period p
    at = [[[model.arithm(visits[p][b], "=", h).reify() for h in range(n_boats)]
           for b in range(n_boats)] for p in range(n_periods)]

    # The crew of a host boat stays on its own boat in every period.
    for b in range(n_boats):
        for p in range(n_periods):
            model.arithm(is_host[b], "<=", at[p][b][b]).post()

    # The people aboard a boat, host crew included, do not exceed its capacity in any period.
    for p in range(n_periods):
        # load[h] is the number of people aboard boat h in period p
        load = [model.intvar(0, capacity[h], name=f"load_{p}_{h}") for h in range(n_boats)]
        model.bin_packing(visits[p], crew_size, load).post()

    # Nobody is aboard a boat that is not a host.
    for p in range(n_periods):
        for b in range(n_boats):
            for h in range(n_boats):
                model.arithm(at[p][b][h], "<=", is_host[h]).post()

    # A guest crew never visits the same boat in two periods.
    for b in range(n_boats):
        for h in range(n_boats):
            if h != b:
                model.sum([at[p][b][h] for p in range(n_periods)], "<=", 1).post()

    # Two crews meet in at most one period, so they share a boat in at most one period.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            # meet[p] is true when crews c1 and c2 are on the same boat in period p
            meet = [model.arithm(visits[p][c1], "=", visits[p][c2]).reify() for p in range(n_periods)]
            model.sum(meet, "<=", 1).post()

    # In each period everyone is aboard a host, so the host boats together hold all the people.
    model.scalar(is_host, capacity, ">=", sum(crew_size)).post()

    # n_hosts is the number of host boats. A guest crew visits a different host in every
    # period, so there are at least n_periods hosts, unless every boat is a host.
    n_hosts = model.intvar(min(n_periods, n_boats), n_boats, name="n_hosts")
    model.sum(is_host, "=", n_hosts).post()

    # Use as few host boats as possible.
    return model, {"visits": visits, "is_host": is_host}, {"objective": n_hosts, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
