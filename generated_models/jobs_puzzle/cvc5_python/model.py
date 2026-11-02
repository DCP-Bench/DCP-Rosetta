# jobs_puzzle: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install cvc5 numpy`) with:
#   python jobs_puzzle.py

import cvc5.pythonic as c5


def create_model(instance):
    """Four people hold eight different jobs, two jobs each. Five clues say who cannot hold
    which job. Find the person, numbered 0 to 3, who holds each job."""
    n_people = 4  # people 0 to 3
    jobs_per_person = 2  # each person holds exactly two jobs

    # the eight jobs
    jobs = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    # held_by[job]: the person who holds the job
    held_by = {job: c5.Int(job) for job in jobs}

    # the conditions the assignment must meet
    solver = c5.Solver()

    # Each job is held by one of the four people.
    for job in jobs:
        solver.add(held_by[job] >= 0, held_by[job] <= n_people - 1)

    # Each person holds exactly two jobs.
    for person in range(n_people):
        solver.add(
            c5.Sum([c5.If(held_by[job] == person, 1, 0) for job in jobs]) == jobs_per_person
        )

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    solver.add([held_by["nurse"] != held_by[job] for job in ["teacher", "police_officer", "clerk"]])

    # Clue 2: the clerk is not the chef.
    solver.add(held_by["clerk"] != held_by["chef"])

    # Clue 3: person 0 is not the boxer.
    solver.add(held_by["boxer"] != 0)

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    solver.add([held_by[job] != 3 for job in ["teacher", "police_officer", "nurse"]])

    # Clue 5: person 0, the chef and the police officer went golfing together. The chef and
    # the police officer are not person 0, and they are different people.
    solver.add(
        held_by["chef"] != 0,
        held_by["police_officer"] != 0,
        held_by["chef"] != held_by["police_officer"],
    )

    return solver, {job: held_by[job] for job in jobs}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
