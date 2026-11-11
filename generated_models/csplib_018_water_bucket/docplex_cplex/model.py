# csplib_018_water_bucket: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

from docplex.mp.model import Model


def create_model(instance):
    """Water bucket: divide the water by pouring between buckets of given capacities. A transfer
    pours water from one bucket into another until the first is empty or the second is full;
    find the fewest transfers that reach the goal amounts. The plan is a sequence of MAX_STEPS
    states: once the goal is reached, the remaining states are padding states with every amount
    equal to the padding value."""
    capacities = instance["capacities"]        # capacities[b]: the capacity of bucket b
    initial_state = instance["initial_state"]  # initial_state[b]: the water in bucket b at the start
    goal_state = instance["goal_state"]        # goal_state[b]: the water wanted in bucket b
    max_steps = instance["MAX_STEPS"]          # the length of the sequence of states
    pad = instance["PADDING_VALUE"]            # every amount of a padding state
    n_buckets = len(capacities)
    steps = range(max_steps)

    # Pouring only moves water between the three buckets, so the total never changes. A state is
    # a split (i, j, k) of that total with each amount within its bucket's capacity.
    total_water = sum(initial_state)
    states = []
    for i in range(capacities[0] + 1):
        for j in range(capacities[1] + 1):
            k = total_water - i - j
            if 0 <= k <= capacities[2]:
                states.append((i, j, k))

    # The valid pourings: pour from bucket a into bucket b until a is empty or b is full,
    # moving a positive amount.
    successors = {state: set() for state in states}
    for state in states:
        for a in range(n_buckets):
            for b in range(n_buckets):
                if a == b:
                    continue
                amount = min(state[a], capacities[b] - state[b])
                if amount > 0:
                    after = list(state)
                    after[a] -= amount
                    after[b] += amount
                    successors[state].add(tuple(after))

    start = tuple(initial_state)
    goal = tuple(goal_state)
    index = {s: q for q, s in enumerate(states)}
    PAD = len(states)  # index of the padding state
    options = range(len(states) + 1)

    model = Model("water_bucket")

    # at[t, q] is 1 when step t is in state q (or padding, q == PAD); one state per step.
    at = model.binary_var_matrix(steps, options, name="at")
    model.add_constraints(model.sum(at[t, q] for q in options) == 1 for t in steps)

    # The sequence starts with the initial state.
    model.add_constraint(at[0, index[start]] == 1)

    for t in range(max_steps - 1):
        for s in states:
            q = index[s]
            if s == goal:
                # After the goal, the next state is padding.
                model.add_constraint(at[t, q] <= at[t + 1, PAD])
            else:
                # Otherwise a transfer happens: the next state is one valid pouring away,
                # which always changes the state.
                model.add_constraint(
                    at[t, q] <= model.sum(at[t + 1, index[n]] for n in successors.get(s, ())
                                          if n in index))
        # After padding, the next state is padding.
        model.add_constraint(at[t, PAD] <= at[t + 1, PAD])

    # The goal is reached at some step.
    model.add_constraint(model.sum(at[t, index[goal]] for t in steps) >= 1)

    # sequence[t][b] is the amount in bucket b at step t, or the padding value.
    sequence = [[model.sum(s[b] * at[t, index[s]] for s in states if s[b] != 0)
                 + pad * at[t, PAD] for b in range(n_buckets)] for t in steps]

    # The cost is the number of transfers: the number of steps before padding, minus one.
    cost = model.integer_var(0, max_steps - 1, name="cost")
    model.add_constraint(cost == model.sum(1 - at[t, PAD] for t in steps) - 1)
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}


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
