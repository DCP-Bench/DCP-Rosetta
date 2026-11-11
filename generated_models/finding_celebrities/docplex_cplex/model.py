# finding_celebrities: a CPLEX (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python finding_celebrities.py finding_celebrities.json

from docplex.mp.model import Model


def create_model(instance):
    """Celebrities: find the people everybody knows and who know only other celebrities; there is at least one."""
    graph = instance["graph"]  # graph[i][j] is 1 if person i knows person j (everyone knows themselves)
    n = len(graph)
    people = range(n)
    known_by = [sum(graph[j][i] for j in people) for i in people]  # how many people know i
    knows = [sum(graph[i][j] for j in people) for i in people]     # how many people i knows

    model = Model("finding_celebrities")

    # celebrities[i] is 1 when person i is a celebrity.
    celebrities = model.binary_var_list(n, name="celebrities")

    # n_celebrities is the number of celebrities; at least one is present.
    n_celebrities = model.integer_var(1, n, name="n_celebrities")
    model.add_constraint(model.sum(celebrities) == n_celebrities)

    # Everybody knows each celebrity, so a celebrity knows all the celebrities, and only them:
    # a person known by everybody is a celebrity exactly when the number of people they know is
    # the number of celebrities. A person some guest does not know is not a celebrity.
    for i in people:
        if known_by[i] == n:
            model.add_equivalence(celebrities[i], n_celebrities == knows[i])
        else:
            model.add_constraint(celebrities[i] == 0)

    return model, {"celebrities": celebrities}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
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
