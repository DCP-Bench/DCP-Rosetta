# just_forgotten: a hermax (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install hermax`):
#   python just_forgotten.py just_forgotten.json

from hermax.model import Model


def create_model(instance):
    """Joe's forgotten account number uses each digit 0 to n-1 exactly once. Each set he
    tried has a fixed number of digits in the same position as the account number, and
    those counts determine the account number. Find it."""
    sets = instance["sets"]  # sets[k] is the k-th digit sequence Joe tried
    num_correct = instance["num_correct_digits"]  # how many digits of each set are in the right place
    n = len(sets[0])  # number of digits in the account number, read from the data

    m = Model()

    # account[i] is the digit at position i of the account number
    account = m.int_vector("account", n, 0, n - 1)

    # The account number uses each digit from 0 to n-1 exactly once.
    m &= account.all_different()

    # Each tried set agrees with the account number in exactly num_correct positions.
    for tried in sets:
        m &= (sum(1 * (account[i] == tried[i]) for i in range(n)) == num_correct)

    # No objective: any account number that fits every set is a solution.
    return m, {"x": account}


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
