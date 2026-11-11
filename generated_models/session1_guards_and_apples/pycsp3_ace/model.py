# session1_guards_and_apples: a PyCSP3 model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from pycsp3 import *


def create_model(instance):
    """A boy passes a number of gates to give an apple to a girl. Each gate has a guard, and he
    bribes each guard with half of his apples, plus one. He gives an integer number of apples,
    and after the last gate he has exactly one apple left. How many apples does he have before
    each gate, and after the last gate?"""
    num_gates = instance["num_gates"]  # the number of gates, each with a guard
    n_counts = num_gates + 1           # apples before each gate, then after the last gate

    # The apples are never more than the count before the first gate. Working back from one apple
    # after the last gate, each gate doubles the count and adds 2 (the bribe is half plus one, so
    # the count before a gate is twice the count after it plus 2). The count before the first gate
    # is then 3 * 2**num_gates - 2, which bounds every count.
    max_apples = 3 * 2**num_gates - 2

    # apples[i] is the number of apples before gate i, and apples[num_gates] the number after the last gate
    apples = VarArray(size=n_counts, dom=range(max_apples + 1))

    satisfy(
        # Before each gate the boy has apples[i]. He gives the guard half of them plus one,
        # so apples[i] is even, and keeps apples[i] - (apples[i] / 2 + 1) = apples[i + 1].
        # Solved for apples[i] that is 2 * (apples[i + 1] + 1).
        [apples[i] == 2 * (apples[i + 1] + 1) for i in range(num_gates)],
        # After the last gate he has exactly one apple, which he gives to the girl.
        apples[num_gates] == 1,
    )

    return {"apples": apples}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
