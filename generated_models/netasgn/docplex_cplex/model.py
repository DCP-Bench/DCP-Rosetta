# netasgn: a CPLEX (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python netasgn.py netasgn.json

from docplex.mp.model import Model


def create_model(instance):
    """Project assignment: split each person's hours over the projects to meet every demand at the least cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]    # cost[i][j]: hourly cost of person i on project j
    limit = instance["limit"]  # limit[i][j]: most hours person i may work on project j
    people = range(len(supply))
    projects = range(len(demand))

    model = Model("netasgn")

    # assign[i, j] is the hours person i works on project j, at most limit[i][j].
    assign = {(i, j): model.integer_var(0, limit[i][j], name=f"assign_{i}_{j}")
              for i in people for j in projects}

    # Each person works exactly their available hours.
    model.add_constraints(model.sum(assign[i, j] for j in projects) == supply[i] for i in people)

    # Each project receives exactly the hours it requires.
    model.add_constraints(model.sum(assign[i, j] for i in people) == demand[j] for j in projects)

    # Minimise the total cost of the hours assigned.
    total_cost = model.sum(cost[i][j] * assign[i, j] for i in people for j in projects)
    model.minimize(total_cost)

    return model, {"assign": [[assign[i, j] for j in projects] for i in people], "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
