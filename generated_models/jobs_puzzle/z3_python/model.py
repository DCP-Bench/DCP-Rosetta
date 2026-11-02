# jobs_puzzle: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install z3-solver numpy`) with:
#   python jobs_puzzle.py

import z3


def create_model(instance):
    """Four people hold eight different jobs, two jobs each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues say who cannot hold which job.
    Find which person holds which job."""
    n_people = 4  # people 0 to 3
    n_jobs = 8

    # Each variable is the person who holds that job.
    jobs = z3.IntVector("job", n_jobs)
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

    solver = z3.Solver()

    # Each job is held by one of the people.
    solver.add([z3.And(0 <= job, job < n_people) for job in jobs])

    # Each person holds exactly two jobs.
    solver.add([z3.PbEq([(job == person, 1) for job in jobs], 2) for person in range(n_people)])

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    solver.add(nurse != teacher, nurse != police_officer, nurse != clerk)

    # Clue 2: the clerk is not the chef.
    solver.add(clerk != chef)

    # Clue 3: person 0 is not the boxer.
    solver.add(boxer != 0)

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    solver.add(teacher != 3, police_officer != 3, nurse != 3)

    # Clue 5: person 0, the chef and the police officer went golfing together,
    # so they are three different people.
    solver.add(chef != 0, police_officer != 0, chef != police_officer)

    return solver, {
        "chef": chef, "guard": guard, "nurse": nurse, "clerk": clerk,
        "police_officer": police_officer, "teacher": teacher, "actor": actor,
        "boxer": boxer,
    }


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
