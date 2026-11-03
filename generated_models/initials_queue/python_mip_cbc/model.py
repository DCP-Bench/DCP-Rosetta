# initials_queue: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install mip numpy`) with:
#   python initials_queue.py

import mip

n_letters = 5  # the letters A to E, numbered 0 to 4
# Every pair of distinct letters, in alphabetical order: the possible initials.
PAIRS = [(a, b) for a in range(n_letters) for b in range(a + 1, n_letters)]
n_people = len(PAIRS)  # one person for each pair


def create_model(instance):
    """Ten people stand in a queue for a Maths lecture. Each has two different initials from A to E,
    in alphabetical order, and no two people have the same initials. No one shares a letter with the
    person in front. BE is at the front, CD right behind, and BD at the back. What are the initials
    of the ten people, from the front?"""
    model = mip.Model(solver_name="CBC")

    # Initials given in the statement, as (first, second) letter numbers: BE at the front,
    # CD behind it, and BD at the back.
    known = {0: (1, 4), 1: (2, 3), n_people - 1: (1, 3)}

    # x[p][s] is 1 when the person at place p in the queue has the initials of pair s.
    x = [[model.add_var(f"x_{p}_{s}", var_type=mip.BINARY,
                        lb=1 if known.get(p) == PAIRS[s] else 0)
          for s in range(n_people)] for p in range(n_people)]

    # Each person has exactly one pair of initials.
    for p in range(n_people):
        model += mip.xsum(x[p][s] for s in range(n_people)) == 1

    # Each pair of initials belongs to exactly one person.
    for s in range(n_people):
        model += mip.xsum(x[p][s] for p in range(n_people)) == 1

    # has_letter[p][L] is 1 when the initials of the person at place p contain letter L.
    has_letter = [[mip.xsum(x[p][s] for s in range(n_people) if L in PAIRS[s])
                   for L in range(n_letters)] for p in range(n_people)]

    # Neighbours in the queue share no letter.
    for p in range(n_people - 1):
        for L in range(n_letters):
            model += has_letter[p][L] + has_letter[p + 1][L] <= 1

    # queue[p][k] is the k-th letter of the initials of the person at place p, numbered 0 to 4.
    queue = [[model.add_var(f"queue_{p}_{k}", lb=0, ub=n_letters - 1, var_type=mip.INTEGER)
              for k in range(2)] for p in range(n_people)]
    for p in range(n_people):
        model += queue[p][0] == mip.xsum(PAIRS[s][0] * x[p][s] for s in range(n_people))
        model += queue[p][1] == mip.xsum(PAIRS[s][1] * x[p][s] for s in range(n_people))

    return model, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
