# Program shape (DOcplex in Python)

Back to [README](README.md) · [SKILL.md](../../SKILL.md)

A model is usually a script that reads its data, solves, and prints the answer. Here the data
file is a JSON file named on the command line (`python3 knapsack.py data.json`); any format your
own program can read works the same way:

```python
import json
import sys

from docplex.mp.model import Model

with open(sys.argv[1]) as f:                  # data file named on the command line
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]

m = Model(name="knapsack")
m.parameters.mip.tolerances.mipgap = 0        # exact optimum, see Solving
take = m.binary_var_list(len(weights), name="take")
m.add_constraint(m.scal_prod(take, weights) <= capacity, ctname="capacity")
m.maximize(m.scal_prod(take, values))

sol = m.solve()
status = m.solve_details.status
if sol is None:
    if status == "integer infeasible":
        print("No selection fits: the model is infeasible")
    else:
        raise SystemExit(f"no answer: {status}")         # never print a guess
elif status != "integer optimal solution":
    raise SystemExit(f"optimum not proven: {status}")
else:
    chosen = [i for i, t in enumerate(take) if round(sol[t]) == 1]
    print(f"Best value {round(sol.objective_value)}: take items {chosen}")
```

Three rules this shape follows:

- Read the status string after `solve()`, never only `None`. `None` covers infeasible, unbounded
  and stopped-without-a-solution.
- Report a solution as the answer only when its status is `integer optimal solution`. A feasible
  model with no objective also reports that status, so one check covers optimisation and
  satisfaction.
- Exit non-zero (`SystemExit` with a message) for every other case, so no guess is printed.

[Product mix](../../assets/python/product-mix/model.py) and [set cover](../../assets/python/set-cover/model.py) show
the optimisation side, and [infeasible staffing](../../assets/python/infeasible-staffing/model.py) shows reading
the infeasible status without an exception.
