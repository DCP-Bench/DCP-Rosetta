# devils_word: a CPLEX (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python devils_word.py devils_word.json

from docplex.mp.model import Model


def create_model(instance):
    """Devil's word: give each number of a list (the character codes of a name) a plus or a minus
    sign so that the signed numbers add up to the target total (666)."""
    arr = instance["arr"]      # the numbers to sign
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)

    model = Model("devils_word")

    # plus[i] is 1 when arr[i] gets a plus sign and 0 when it gets a minus sign
    plus = model.binary_var_list(n, name="plus")

    # result[i] is the number with its sign: arr[i] when added, -arr[i] when subtracted.
    result = [arr[i] * (2 * plus[i] - 1) for i in range(n)]

    # The signed numbers add up to the total.
    model.add_constraint(model.sum(result) == total)

    return model, {"result": result}


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
