# session1_guards_and_apples: a CPLEX (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from docplex.mp.model import Model


def create_model(instance):
    """A boy passes a number of gates, each with a guard he bribes with half of his apples plus one,
    an integer number of apples. After the last gate he has exactly one apple, for the girl.
    Find the number of apples he has before each gate and after the last gate."""
    gates = instance["num_gates"]  # the number of gates the boy passes

    model = Model("guards_and_apples")

    # apples[i] is the number of apples he has before gate i, and apples[gates] the number after
    # the last gate. No upper bound is given: the equations below fix every value.
    apples = model.integer_var_list(gates + 1, 0, name="apples")

    # After the last gate he has the one apple he gives to the girl.
    model.add_constraint(apples[gates] == 1, ctname="for_the_girl")

    # Each guard takes half of the apples plus one, so what he had was twice
    # what he keeps plus two.
    model.add_constraints(apples[i - 1] == 2 * (apples[i] + 1) for i in range(1, gates + 1))

    return model, {"apples": apples}


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
