# jobs_puzzle: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install pulp numpy`) with:
#   python jobs_puzzle.py

import pulp


def create_model(instance):
    """Four people hold eight different jobs, two each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues say who cannot hold which job.
    Find the person, 0 to 3, who holds each job."""
    people = range(4)
    jobs = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    # The person and job pairs that the clues rule out: clues 3, 4 and 5.
    ruled_out = {"boxer": [0], "teacher": [3], "police_officer": [0, 3], "nurse": [3], "chef": [0]}

    problem = pulp.LpProblem("jobs_puzzle", pulp.LpMinimize)

    # holds[job][p] is 1 when person p holds the job, and 0 when not.
    holds = {
        job: [pulp.LpVariable(f"holds_{job}_{p}", 0, 0 if p in ruled_out.get(job, []) else 1,
                              cat="Integer")
              for p in people]
        for job in jobs
    }

    # Each job has one holder.
    for job in jobs:
        problem += pulp.lpSum(holds[job]) == 1

    # Each person holds exactly two jobs.
    for p in people:
        problem += pulp.lpSum(holds[job][p] for job in jobs) == 2

    # The two jobs are held by different people.
    def different(job1, job2):
        for p in people:
            problem.addConstraint(holds[job1][p] + holds[job2][p] <= 1)

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    for other in ("teacher", "police_officer", "clerk"):
        different("nurse", other)

    # Clue 2: the clerk is not the chef.
    different("clerk", "chef")

    # Clue 5: the chef and the police officer are different people.
    different("chef", "police_officer")

    return problem, {
        job: pulp.lpSum(p * var for p, var in zip(people, holds[job])) for job in jobs
    }


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
