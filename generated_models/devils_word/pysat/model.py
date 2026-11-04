# devils_word: a PySAT (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python devils_word.py devils_word.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Put a plus or a minus sign in front of every number of a list so that the
    signed numbers add up to the given total."""
    arr = instance["arr"]      # the numbers, in order
    total = instance["total"]  # the value the signed numbers must add up to

    pool = IDPool()  # names the variables of the model

    # plus[i] is true when arr[i] gets a plus sign and false when it gets a minus sign
    plus = [pool.id(("plus", i)) for i in range(len(arr))]
    # result[i] is arr[i] with its sign, so it lies between -arr[i] and arr[i]
    result = [Integer(f"result_{i}", -abs(arr[i]), abs(arr[i]), vpool=pool)
              for i in range(len(arr))]
    engine = IntegerEngine(vars=result, vpool=pool)  # the constraints on the signed numbers
    formula = engine.clausify()

    # A number with a plus sign stays as it is, a number with a minus sign is negated.
    for i in range(len(arr)):
        formula.append([-plus[i], result[i].equals(arr[i])])
        formula.append([plus[i], result[i].equals(-arr[i])])

    # The signed numbers add up to the total. Twice the sum of the numbers with a plus
    # sign equals the total plus the sum of all numbers.
    formula.extend(PBEnc.equals(lits=plus, weights=[2 * value for value in arr],
                                bound=total + sum(arr), vpool=pool).clauses)

    return formula, {"result": result}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
