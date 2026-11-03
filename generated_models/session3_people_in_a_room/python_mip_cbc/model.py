# session3_people_in_a_room: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install mip numpy`) with:
#   python session3_people_in_a_room.py

import mip


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    n_people = 13  # the number of people
    n_males = 4    # the number of men among them
    n_females = n_people - n_males

    model = mip.Model(solver_name="CBC")

    # sequence[i] is 1 when the i-th person to enter is female, and 0 when male.
    sequence = [model.add_var(f"sequence_{i}", var_type=mip.BINARY) for i in range(n_people)]

    # Exactly n_females of the people are female.
    model.add_constr(mip.xsum(sequence) == n_females)

    for t in range(n_people):
        # Females and males in the room after the first t + 1 entries.
        females = mip.xsum(sequence[: t + 1])
        males = (t + 1) - females
        # The females are at most 7/3 of the males, written as 3 * females <= 7 * males.
        model.add_constr(3 * females <= 7 * males)

    return model, {"sequence": sequence}


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
