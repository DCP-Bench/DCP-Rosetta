# jobs_puzzle: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python jobs_puzzle.py

from docplex.mp.model import Model


def create_model(instance):
    """Jobs puzzle: four people hold eight different jobs, two each. From five clues, find who
    holds which job."""
    num_people = 4  # the people are numbered 0..3
    jobs_per_person = 2  # each person holds exactly two jobs
    names = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
    people = range(num_people)

    model = Model("jobs_puzzle")

    # holds[j, p] is 1 when person p holds job j; every job has one holder.
    holds = {(j, p): model.binary_var(name=f"{j}_held_by_{p}") for j in names for p in people}
    model.add_constraints(model.sum(holds[j, p] for p in people) == 1 for j in names)

    # Each person holds exactly two jobs.
    model.add_constraints(model.sum(holds[j, p] for j in names) == jobs_per_person for p in people)

    def different(j1, j2):
        # Jobs j1 and j2 have different holders: no person holds both.
        model.add_constraints(holds[j1, p] + holds[j2, p] <= 1 for p in people)

    def not_held_by(j, p):
        model.add_constraint(holds[j, p] == 0)

    # 1. The nurse is not the teacher, the police officer or the clerk.
    different("nurse", "teacher")
    different("nurse", "police_officer")
    different("nurse", "clerk")
    # 2. The clerk is not the chef.
    different("clerk", "chef")
    # 3. Person 0 is not the boxer.
    not_held_by("boxer", 0)
    # 4. Person 3 is not the teacher, the police officer or the nurse.
    not_held_by("teacher", 3)
    not_held_by("police_officer", 3)
    not_held_by("nurse", 3)
    # 5. Person 0, the chef and the police officer went golfing together: three different
    # people.
    not_held_by("chef", 0)
    not_held_by("police_officer", 0)
    different("chef", "police_officer")

    # holder[j] is the person (0..num_people - 1) who holds job j.
    holder = {j: model.sum(p * holds[j, p] for p in people) for j in names}

    return model, holder


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
