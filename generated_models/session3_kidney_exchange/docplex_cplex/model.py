# session3_kidney_exchange: a CPLEX (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from docplex.mp.model import Model


def create_model(instance):
    """Kidney exchange: people on a waiting list can donate a kidney to the people compatible
    with them. Arrange the donations so that as many people as possible receive a kidney: anyone
    who gives a kidney must receive one, and no person receives more than one kidney."""
    n = instance["num_people"]  # the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people, 1-based, i can donate to
    people = range(n)

    model = Model("kidney_exchange")

    # transplants[i, j] is 1 when person i donates to person j. A donation to
    # someone i is not compatible with gets an upper bound of 0.
    transplants = model.binary_var_matrix(people, people, name="transplants")
    for i in people:
        for j in people:
            if j + 1 not in compatible[i]:
                transplants[i, j].ub = 0

    for i in people:
        gives = model.sum(transplants[i, j] for j in people)
        receives = model.sum(transplants[j, i] for j in people)
        # No person receives more than one kidney.
        model.add_constraint(receives <= 1, ctname=f"receive_once_{i}")
        # Anyone who gives a kidney must receive one (which also limits giving to one kidney).
        model.add_constraint(gives <= receives, ctname=f"gives_receives_{i}")

    # Maximise the number of people who receive a new kidney (one per transplant).
    model.maximize(model.sum(transplants.values()))

    return model, {"transplants": [[transplants[i, j] for j in people] for i in people]}


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
