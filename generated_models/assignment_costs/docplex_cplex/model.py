# assignment_costs: a CPLEX (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python assignment_costs.py assignment_costs.json

from docplex.mp.model import Model


def create_model(instance):
    """Assignment: give every task to a different person at the least total cost; people may stay idle."""
    cost = instance["cost"]  # cost[i][j]: cost of person j doing task i
    tasks = range(len(cost))
    people = range(len(cost[0]))

    model = Model("assignment_costs")

    # x[i, j] is 1 when task i is assigned to person j.
    x = model.binary_var_matrix(tasks, people, name="x")

    # Each task is assigned to exactly one person.
    model.add_constraints(model.sum(x[i, j] for j in people) == 1 for i in tasks)

    # Each person takes at most one task (some people may stay without a task).
    model.add_constraints(model.sum(x[i, j] for i in tasks) <= 1 for j in people)

    # Minimise the total cost of the assignment.
    model.minimize(model.sum(cost[i][j] * x[i, j] for i in tasks for j in people))

    return model, {"x": [[x[i, j] for j in people] for i in tasks]}


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
