# csplib_013_progressive_party_problem: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from docplex.mp.model import Model


def create_model(instance):
    """Progressive party: timetable a party at a yacht club. Certain boats are designated hosts,
    and the crews of the remaining boats visit the host boats in successive periods. The people
    aboard a boat (host crew and guest crews) must not exceed its capacity, a guest crew cannot
    revisit a host and two crews cannot meet more than once. Minimize the number of host boats."""
    n_boats = instance["n_boats"]      # number of boats, each with its own crew
    n_periods = instance["n_periods"]  # number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: most people aboard boat b at a time
    crew_size = instance["crew_size"]  # crew_size[b]: people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    model = Model("progressive_party")
    # The meeting rule below is a quadratic constraint over binaries, which is not convex.
    # CPLEX refuses such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # is_host[b] is 1 when boat b is a host boat.
    is_host = model.binary_var_list(n_boats, name="is_host")

    # at[p, c, b] is 1 when the crew of boat c is aboard boat b in period p.
    at = model.binary_var_cube(periods, boats, boats, name="at")

    # In every period each crew is aboard exactly one boat.
    model.add_constraints(model.sum(at[p, c, b] for b in boats) == 1 for p in periods for c in boats)

    # Crews of host boats stay on their own boat in every period.
    model.add_constraints(at[p, b, b] >= is_host[b] for p in periods for b in boats)

    # Only host boats can be visited: at most n_boats crews are aboard a boat, and none unless it is
    # a host. One row per boat and period, summed over the crews, instead of one per crew (to stay
    # within the Community Edition's limit of 1000 constraints).
    model.add_constraints(model.sum(at[p, c, b] for c in boats) <= n_boats * is_host[b]
                          for p in periods for b in boats)

    # The people aboard a boat in a period never exceed its capacity.
    model.add_constraints(model.sum(crew_size[c] * at[p, c, b] for c in boats) <= capacity[b]
                          for p in periods for b in boats)

    # A guest crew cannot visit the same boat twice.
    model.add_constraints(model.sum(at[p, c, b] for p in periods) <= 1
                          for c in boats for b in boats if b != c)

    # Two crews cannot be together more than once: the number of (period, boat) pairs in
    # which both crews are aboard the same boat is at most 1. One quadratic constraint per
    # pair of crews; the linear alternative needs one row per pair, period and boat.
    for c1 in boats:
        for c2 in range(c1 + 1, n_boats):
            meetings = model.sum(at[p, c1, b] * at[p, c2, b] for p in periods for b in boats)
            model.add_constraint(meetings <= 1)

    # Minimize the number of host boats.
    model.minimize(model.sum(is_host))

    # visits[p][c] is the boat that the crew of boat c is aboard in period p.
    visits = [[model.sum(b * at[p, c, b] for b in boats) for c in boats] for p in periods]
    return model, {"visits": visits, "is_host": is_host}


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
