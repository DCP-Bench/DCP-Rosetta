# jobs_puzzle: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install pychoco numpy`) with:
#   python jobs_puzzle.py

from pychoco.model import Model


def create_model(instance):
    """Four people hold eight different jobs, two each: chef, guard, nurse, clerk,
    police officer, teacher, actor and boxer. Five clues say who cannot hold which job.
    Find which person holds which job."""
    # Four people, numbered 0 to 3.
    n_people = 4
    people = list(range(n_people))

    # The eight jobs.
    job_names = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]

    model = Model()

    # job[name] is the person who holds that job.
    job = {name: model.intvar(0, n_people - 1, name=name) for name in job_names}

    # held[p] is how many jobs person p holds.
    held = [model.intvar(2, 2, name=f"held_{p}") for p in people]

    # Each person holds exactly two jobs.
    model.global_cardinality([job[name] for name in job_names], people, held).post()

    # Clue 1: the nurse is not the teacher, the police officer or the clerk.
    for other in ("teacher", "police_officer", "clerk"):
        model.arithm(job["nurse"], "!=", job[other]).post()

    # Clue 2: the clerk is not the chef.
    model.arithm(job["clerk"], "!=", job["chef"]).post()

    # Clue 3: person 0 is not the boxer.
    model.arithm(job["boxer"], "!=", 0).post()

    # Clue 4: person 3 is not the teacher, the police officer or the nurse.
    for name in ("teacher", "police_officer", "nurse"):
        model.arithm(job[name], "!=", 3).post()

    # Clue 5: person 0, the chef and the police officer went golfing together, so the
    # chef and the police officer are both not person 0, and they are not the same person.
    model.arithm(job["chef"], "!=", 0).post()
    model.arithm(job["police_officer"], "!=", 0).post()
    model.arithm(job["chef"], "!=", job["police_officer"]).post()

    return model, job, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
