# csplib_013_progressive_party_problem: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

import mip


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # is_host[b] is 1 when boat b is a host boat, and 0 when not
    is_host = [model.add_var(f"is_host_{b}", var_type=mip.BINARY) for b in range(n_boats)]
    # at[p][b][h] is 1 when the crew of boat b is aboard boat h in period p
    at = [
        [[model.add_var(f"at_{p}_{b}_{h}", var_type=mip.BINARY) for h in range(n_boats)]
         for b in range(n_boats)]
        for p in range(n_periods)
    ]

    for p in range(n_periods):
        for b in range(n_boats):
            # Each crew is aboard exactly one boat in each period.
            model.add_constr(mip.xsum(at[p][b][h] for h in range(n_boats)) == 1)
            # The crew of a host boat stays aboard its own boat, and a guest crew does not.
            model.add_constr(at[p][b][b] == is_host[b])
            # A host crew does not go aboard any other boat.
            for h in range(n_boats):
                if h != b:
                    model.add_constr(at[p][b][h] <= 1 - is_host[b])

    # The people aboard boat h in each period, host crew included, do not exceed its capacity.
    # A boat that is not a host has no capacity, so it holds nobody.
    for p in range(n_periods):
        for h in range(n_boats):
            model.add_constr(
                mip.xsum(crew_size[b] * at[p][b][h] for b in range(n_boats)) <= capacity[h] * is_host[h]
            )
            # With an empty crew, the capacity row does not stop it boarding a boat that is not a host.
            if min(crew_size) == 0:
                for b in range(n_boats):
                    model.add_constr(at[p][b][h] <= is_host[h])

    # A guest crew does not revisit a host boat.
    for b in range(n_boats):
        for h in range(n_boats):
            if h != b:
                model.add_constr(mip.xsum(at[p][b][h] for p in range(n_periods)) <= 1)

    # Each guest crew visits a different host in each period, so there are at least as many
    # hosts as periods (or all boats, if there are fewer). The host capacities must also hold
    # everyone, so at least as many hosts as the fewest largest capacities that add up to all
    # the people are needed.
    total_people = sum(crew_size)  # the people in all crews together
    min_hosts_by_capacity = n_boats
    people_held = 0  # the capacity of the largest boats added up so far
    for k, c in enumerate(sorted(capacity, reverse=True), start=1):
        people_held += c
        if people_held >= total_people:
            min_hosts_by_capacity = k
            break
    model.add_constr(mip.xsum(is_host) >= max(min(n_boats, n_periods), min_hosts_by_capacity))

    # Crews a and b meet when both are aboard the same boat in the same period, and two crews
    # meet at most once.
    for a in range(n_boats):
        for b in range(a + 1, n_boats):
            meetings = []  # the together variables of crews a and b, one per period and boat
            for p in range(n_periods):
                for h in range(n_boats):
                    # together is at least 1 when crews a and b are both aboard boat h in period p.
                    together = model.add_var(f"together_{p}_{a}_{b}_{h}", lb=0, ub=1)
                    model.add_constr(together >= at[p][a][h] + at[p][b][h] - 1)
                    meetings.append(together)
            model.add_constr(mip.xsum(meetings) <= 1)

    # Minimize the number of host boats.
    model.objective = mip.xsum(is_host)

    # visits[p][b] is the boat that the crew of boat b is aboard in period p, 0-based.
    visits = [
        [mip.xsum(h * at[p][b][h] for h in range(n_boats)) for b in range(n_boats)]
        for p in range(n_periods)
    ]

    return model, {"is_host": is_host, "visits": visits}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
