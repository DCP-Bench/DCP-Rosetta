# devils_word: a hermax (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install hermax`):
#   python devils_word.py devils_word.json

from hermax.model import Model


def create_model(instance):
    """Devil's word: put a plus or minus sign in front of every number of a list so that
    the signed numbers add up to the given total."""
    arr = instance["arr"]      # arr[i]: the i-th number of the list, in order
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)               # one sign per number, whatever the list length

    m = Model()

    # plus[i] is true when arr[i] gets a plus sign and false when it gets a minus sign
    plus = m.bool_vector("plus", n)
    # arr[i] with its chosen sign: +arr[i] when plus[i], -arr[i] otherwise
    signed = [2 * arr[i] * plus[i] - arr[i] for i in range(n)]

    # The signed numbers add up to the total.
    m &= (sum(signed) == total)

    # Satisfaction problem: no objective.
    return m, {"result": signed}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
