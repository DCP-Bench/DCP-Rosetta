# general_store: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install pychoco numpy`) with:
#   python general_store.py

from pychoco.model import Model


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter."""
    # The sixteen words above the line.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"  # the total below the line

    model = Model()

    # The letters on the sign, each once.
    letters = sorted(set("".join(words + [total])))
    # digit[c] is the digit that letter c stands for
    digit = {c: model.intvar(0, 9, name=c) for c in letters}

    # Different letters stand for different digits.
    model.all_different(list(digit.values())).post()

    # weight[c] is the place value of letter c summed over the words above the line,
    # minus its place value in the total.
    weight = {c: 0 for c in letters}
    for word, sign in [(w, 1) for w in words] + [(total, -1)]:
        for place, c in enumerate(reversed(word)):
            weight[c] += sign * 10 ** place

    # The words above the line add up to the total.
    model.scalar([digit[c] for c in letters], [weight[c] for c in letters], "=", 0).post()

    return model, {c: digit[c] for c in letters}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
