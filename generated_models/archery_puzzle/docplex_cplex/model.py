# archery_puzzle: a CPLEX (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python archery_puzzle.py archery_puzzle.json

from docplex.mp.model import Model


def create_model(instance):
    """Archery puzzle: choose how often to hit each target so that the score comes as close as possible to the target score."""
    targets = instance["targets"]  # points for a hit on each target
    goal = instance["target_score"]  # the score the archer aims for

    model = Model("archery_puzzle")

    # With no hits the score misses the goal by goal, so a best score is at most 2 * goal; as every
    # hit scores at least 1 point, no target needs more than that many hits.
    max_score = 2 * goal

    # hits[i] is how many arrows hit target i
    hits = model.integer_var_list(len(targets), 0, max_score, name="hits")

    # The score is the sum of the values of all hits.
    score = model.scal_prod(hits, targets)

    # deviation is how far the score is from the goal, |goal - score|. Two lower bounds suffice
    # because deviation is minimised.
    deviation = model.integer_var(0, max_score, name="deviation")
    model.add_constraint(deviation >= goal - score)
    model.add_constraint(deviation >= score - goal)

    # Come as close to the goal as possible.
    model.minimize(deviation)

    return model, {"hits": hits}


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
