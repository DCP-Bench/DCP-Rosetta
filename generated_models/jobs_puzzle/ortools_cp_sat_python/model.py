# jobs_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install ortools`) with:
#   python jobs_puzzle.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Four people hold eight different jobs, two each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues narrow down who holds which job."""
    # The puzzle gives its own people, jobs and clues.
    n_people = 4  # people 0 to 3
    n_jobs = 8

    model = cp_model.CpModel()

    # jobs[j] is the person (0-3) who holds job j.
    jobs = [model.new_int_var(0, n_people - 1, f"job_{j}") for j in range(n_jobs)]
    chef, guard, nurse, clerk, police_officer, teacher, actor, boxer = jobs

    # Each person holds exactly two jobs.
    for person in range(n_people):
        # holds[j] is true when this person holds job j.
        holds = []
        for j in range(n_jobs):
            holds_j = model.new_bool_var(f"holds_{person}_{j}")
            model.add(jobs[j] == person).only_enforce_if(holds_j)
            model.add(jobs[j] != person).only_enforce_if(~holds_j)
            holds.append(holds_j)
        model.add(sum(holds) == 2)

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
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
