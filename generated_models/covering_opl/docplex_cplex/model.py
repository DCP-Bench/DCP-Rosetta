# covering_opl: a CPLEX (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python covering_opl.py covering_opl.json

from docplex.mp.model import Model


def create_model(instance):
    """Select a set of workers to perform all the tasks at minimum cost: each worker can perform
    certain tasks and has a hiring cost, and every task must be performed."""
    n_workers = instance["nb_workers"]  # number of workers
    cost = instance["Cost"]  # cost[w]: the hiring cost of worker w
    qualified = instance["Qualified"]  # qualified[t]: the workers, numbered from 1, who can perform task t

    model = Model("covering_opl")

    # hire[w] is 1 when worker w is hired, and 0 when not
    hire = model.binary_var_list(n_workers, name="hire")

    # Every task is performed: at least one hired worker is qualified for it (workers are
    # numbered from 1 in qualified).
    model.add_constraints(model.sum(hire[w - 1] for w in workers) >= 1 for workers in qualified)

    # Minimise the total hiring cost.
    total_cost = model.scal_prod(hire, cost)
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "workers": hire}


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
