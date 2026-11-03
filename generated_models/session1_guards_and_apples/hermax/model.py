# session1_guards_and_apples: a hermax (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install hermax`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from hermax.model import Model


def create_model(instance):
    """A boy must pass a number of gates, each with a guard, to give an apple to a girl.
    At each gate he bribes the guard with half of his apples plus one, paying an integer
    number of apples. After the girl gets her apple he has none left. Find how many apples
    he has before each gate, and after the last gate."""
    num_gates = instance["num_gates"]  # num_gates: the number of gates, each with a guard

    m = Model()

    # apples[i] is the number of apples before gate i; apples[num_gates] is what is left
    # after the last gate, which is the one apple he gives to the girl.
    # Working backwards, each gate doubles the count and adds two, so the count before the
    # first gate is at most 3 * 2**num_gates - 2.
    upper = 3 * 2 ** num_gates - 2
    apples = m.int_vector("apples", num_gates + 1, 0, upper)

    # bribe[i] is the number of apples he gives the guard at gate i: half of at most `upper`
    # apples plus one, so at most upper // 2 + 1 = 3 * 2**(num_gates - 1); and at least 1.
    bribe = m.int_vector("bribe", num_gates, 1, upper // 2 + 1)

    # He has one apple left after the last gate, which he gives to the girl.
    m &= (apples[num_gates] == 1)

    for i in range(num_gates):
        # The bribe is half of his apples plus one, and it is a whole number of apples:
        # 2 * bribe[i] = apples[i] + 2, so apples[i] must be even.
        m &= (2 * bribe[i] == apples[i] + 2)
        # What he keeps after paying the guard is what he has before the next gate.
        m &= (apples[i] - bribe[i] == apples[i + 1])

    return m, {"apples": apples}


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
