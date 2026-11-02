# covering_opl: a PySAT (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python covering_opl.py covering_opl.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    nb_workers = instance["nb_workers"]  # the number of workers
    num_tasks = instance["num_tasks"]    # the number of tasks
    qualified = instance["Qualified"]    # qualified[j]: the workers, numbered from 1, who can perform task j
    cost = instance["Cost"]              # cost[i]: the hiring cost of worker i

    pool = IDPool()
    formula = WCNF()

    # workers[i] is true when worker i is hired.
    workers = [pool.id(("workers", i)) for i in range(nb_workers)]

    # Every task is performed by at least one hired worker who is qualified for it.
    for j in range(num_tasks):
        formula.append([workers[c - 1] for c in qualified[j]])

    # The total cost is at most the cost of hiring everyone. It is at least 1, so the
    # range is not empty when no worker costs anything.
    top = max(sum(cost), 1)
    # total_cost is the total hiring cost of the hired workers, a whole number of dollars.
    total_cost = Integer("total_cost", 0, top, encoding="coupled", vpool=pool)
    formula.extend(total_cost.domain_clauses())
    # above[k] is true when the total cost is at least k.
    above = [total_cost.ge(k) for k in range(1, top + 1)]
    # The total cost is the sum of the hiring costs of the hired workers, and it is also
    # the number of levels in above that it reaches.
    formula.extend(PBEnc.equals(lits=workers + above,
                                weights=list(cost) + [-1] * top, bound=0,
                                vpool=pool, encoding=EncType.bdd).clauses)

    # Minimise the total cost: each hired worker adds his hiring cost.
    for i in range(nb_workers):
        if cost[i] > 0:
            formula.append([-workers[i]], weight=cost[i])

    return formula, {"total_cost": total_cost, "workers": workers}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
