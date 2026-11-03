# jobs_puzzle: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install cpmpy`) with:
#   python jobs_puzzle.py

import cpmpy as cp


def create_model(instance):
    """Four people hold eight different jobs, two jobs each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues say who cannot hold which job.
    Find which person holds which job."""
    # The puzzle states its own people, jobs and clues, so the instance is empty.
    num_people = 4  # people 0 to 3
    num_jobs = 8

    # Each variable is the person (0-3) who holds that job.
    jobs = cp.intvar(0, num_people - 1, shape=num_jobs, name="jobs")
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

    model = cp.Model()

    # Each person holds exactly two jobs.
    for person in range(num_people):
        model.add(cp.sum(jobs == person) == 2)

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    model.add(nurse != teacher)
    model.add(nurse != police_officer)
    model.add(nurse != clerk)

    # Clue 2: the clerk is not the chef.
    model.add(clerk != chef)

    # Clue 3: person 0 is not the boxer.
    model.add(boxer != 0)

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    model.add(teacher != 3)
    model.add(police_officer != 3)
    model.add(nurse != 3)

    # Clue 5: person 0, the chef and the police officer went golfing together,
    # so they are three different people.
    model.add(chef != 0)
    model.add(police_officer != 0)
    model.add(chef != police_officer)

    return model, {
        "chef": chef, "guard": guard, "nurse": nurse, "clerk": clerk,
        "police_officer": police_officer, "teacher": teacher,
        "actor": actor, "boxer": boxer,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
