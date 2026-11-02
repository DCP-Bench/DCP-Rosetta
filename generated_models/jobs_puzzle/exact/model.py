# jobs_puzzle: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install exact numpy`) with:
#   python jobs_puzzle.py

from exact import Exact

# the eight jobs
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]


def create_model(instance):
    """Four people hold eight different jobs, two each. Five clues say who does not hold
    which job. Find the person who holds each job."""
    n_people = 4         # the people, numbered 0 to 3
    n_jobs = len(JOBS)   # the eight jobs

    solver = Exact()

    # holds[job][p] is 1 when person p holds the job, and 0 when not.
    holds = {job: [f"{job}_held_by_{p}" for p in range(n_people)] for job in JOBS}

    # Exact identifies its variables by name.
    # job is the number of the person who holds it, 0 to 3.
    for job in JOBS:
        solver.addVariable(job, 0, n_people - 1)
        for var in holds[job]:
            solver.addVariable(var, 0, 1)

    def apart(first, second):
        # The two jobs are held by different people.
        for p in range(n_people):
            solver.addConstraint([(1, holds[first][p]), (1, holds[second][p])], False, 0, True, 1)

    def not_held_by(job, person):
        # The person does not hold the job.
        solver.addConstraint([(1, holds[job][person])], False, 0, True, 0)

    # Each job has exactly one holder.
    for job in JOBS:
        solver.addConstraint([(1, var) for var in holds[job]], True, 1, True, 1)

    # The job's number is the number of its holder.
    for job in JOBS:
        solver.addConstraint([(p, holds[job][p]) for p in range(1, n_people)] + [(-1, job)],
                             True, 0, True, 0)

    # Each person holds exactly two jobs.
    for p in range(n_people):
        solver.addConstraint([(1, holds[job][p]) for job in JOBS], True, 2, True, 2)

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    apart("nurse", "teacher")
    apart("nurse", "police_officer")
    apart("nurse", "clerk")

    # Clue 2: the clerk is not the chef.
    apart("clerk", "chef")

    # Clue 3: person 0 is not the boxer.
    not_held_by("boxer", 0)

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)

    # Clue 5: person 0, the chef and the police officer are three different people.
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    apart("chef", "police_officer")

    return solver, {job: job for job in JOBS}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
