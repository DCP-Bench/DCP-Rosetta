# jobs_puzzle: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install mip numpy`) with:
#   python jobs_puzzle.py

import mip


def create_model(instance):
    """Four people hold eight different jobs, two each. Five clues say who cannot hold
    which job and who did not go golfing with whom. Find the person who holds each job."""
    # The four people are 0 to 3, and these are the eight jobs.
    people = range(4)
    jobs = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    # Clue 3: person 0 is not the boxer.
    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    # Clue 5: person 0 is not the chef or the police officer, since the three of them went golfing together.
    ruled_out = {("boxer", 0), ("teacher", 3), ("police_officer", 3), ("nurse", 3),
                 ("chef", 0), ("police_officer", 0)}

    model = mip.Model(solver_name="CBC")

    # x[j][p] is 1 when person p holds job j, and 0 when not.
    x = {
        j: {
            p: model.add_var(f"x_{j}_{p}", lb=0, ub=0 if (j, p) in ruled_out else 1, var_type=mip.INTEGER)
            for p in people
        }
        for j in jobs
    }
    # holder[j] is the person who holds job j.
    holder = {j: model.add_var(f"holder_{j}", lb=0, ub=max(people), var_type=mip.INTEGER) for j in jobs}

    def different_people(a, b):
        # Jobs a and b are held by two different people.
        for p in people:
            model.add_constr(x[a][p] + x[b][p] <= 1)

    # Each job is held by exactly one person, and holder[j] is that person.
    for j in jobs:
        model.add_constr(mip.xsum(x[j][p] for p in people) == 1)
        model.add_constr(holder[j] == mip.xsum(p * x[j][p] for p in people))

    # Each person holds exactly two jobs.
    for p in people:
        model.add_constr(mip.xsum(x[j][p] for j in jobs) == 2)

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    different_people("nurse", "teacher")
    different_people("nurse", "police_officer")
    different_people("nurse", "clerk")

    # Clue 2: the clerk is not the chef.
    different_people("clerk", "chef")

    # Clue 5: the chef and the police officer are not the same person.
    different_people("chef", "police_officer")

    return model, {j: holder[j] for j in jobs}


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
