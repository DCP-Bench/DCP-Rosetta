# crew: a Gurobi (Python) model from DCP Rosetta.
# Download the `crew.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python crew.py crew.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Assign flight attendants to flights so that every flight gets the crew it needs,
    and no attendant works a flight within the two flights after one already worked."""
    attributes = instance["attributes"]        # attributes[p][k] is 1 when attendant p has skill k (steward, hostess, French, Spanish, German), else 0
    required_crew = instance["required_crew"]  # required_crew[f]: the crew size of flight f, then the minimum number of attendants with each skill
    persons = range(len(attributes))
    flights = range(len(required_crew))
    kinds = range(5)  # the five skills (steward, hostess, French, Spanish, German)

    model = gp.Model("crew")

    # crew[f, p] is 1 when attendant p works flight f, and 0 when not.
    crew = model.addVars(flights, persons, vtype=GRB.BINARY, name="crew")

    # Each flight has exactly the crew size it needs (crew.sum(f, "*") adds crew[f, p] over all attendants p).
    model.addConstrs((crew.sum(f, "*") == required_crew[f][0] for f in flights), name="size")

    # Each flight has at least the required number of attendants with each skill.
    model.addConstrs((gp.quicksum(attributes[p][k] * crew[f, p] for p in persons)
                      >= required_crew[f][k + 1]
                      for f in flights for k in kinds), name="skill")

    # An attendant who works a flight has the next two flights off.
    model.addConstrs((crew[f, p] + crew[f + 1, p] + crew[f + 2, p] <= 1
                      for f in range(len(required_crew) - 2) for p in persons), name="rest")

    # Not in the problem statement: at least one attendant works some flight.
    model.addConstr(crew.sum() >= 1, name="someone_works")

    # crew[f][p] is 1 when attendant p works flight f
    return model, {"crew": [[crew[f, p] for p in persons] for f in flights]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
