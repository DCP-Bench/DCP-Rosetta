# jobs_puzzle: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python jobs_puzzle.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: four people, eight jobs, as stated.
PEOPLE = range(4)
# The eight jobs of the statement.
JOBS = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"]
# Each person holds exactly two jobs (eight jobs shared among four people).
JOBS_PER_PERSON = 2


def create_model(instance):
    """Jobs puzzle: four people hold eight jobs, two each; find who holds which job from five clues."""
    model = gp.Model("jobs_puzzle")

    # holds[job, p] = 1 when person p holds that job.
    holds = model.addVars(JOBS, PEOPLE, vtype=GRB.BINARY, name="holds")
    # Each job has exactly one holder.
    model.addConstrs((holds.sum(job, "*") == 1 for job in JOBS), name="one_holder")

    # Each person holds exactly two jobs.
    model.addConstrs((holds.sum("*", p) == JOBS_PER_PERSON for p in PEOPLE), name="two_jobs")

    # 1. The nurse is not the teacher, the police officer, or the clerk: for each
    #    person, no one holds both the nurse job and the other job.
    for job in ("teacher", "police_officer", "clerk"):
        model.addConstrs((holds["nurse", p] + holds[job, p] <= 1 for p in PEOPLE),
                         name=f"nurse_not_{job}")

    # 2. The clerk is not the chef.
    model.addConstrs((holds["clerk", p] + holds["chef", p] <= 1 for p in PEOPLE), name="clerk_not_chef")

    # 3. Person 0 is not the boxer.
    model.addConstr(holds["boxer", 0] == 0, name="boxer_not_0")

    # 4. Person 3 is not the teacher, police officer, or nurse.
    for job in ("teacher", "police_officer", "nurse"):
        model.addConstr(holds[job, 3] == 0, name=f"{job}_not_3")

    # 5. Person 0, the chef and the police officer went golfing together. Read as
    #    three different people (the statement does not spell this out): person 0 is
    #    neither the chef nor the police officer, and the chef and the police officer differ.
    model.addConstr(holds["chef", 0] == 0, name="chef_not_0")
    model.addConstr(holds["police_officer", 0] == 0, name="police_officer_not_0")
    model.addConstrs((holds["chef", p] + holds["police_officer", p] <= 1 for p in PEOPLE),
                     name="chef_not_police_officer")

    # The person index holding each job.
    return model, {job: gp.quicksum(p * holds[job, p] for p in PEOPLE) for job in JOBS}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
