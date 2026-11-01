# hanging_weights: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install pychoco numpy`) with:
#   python hanging_weights.py

from pychoco.model import Model


def create_model(instance):
    """Thirteen weights A to M, each an integer from 1 to 13, hang from a system of
    bars. Find the weights that make every pivot balance, where the weights on either
    side of a pivot are equal when weighted by their distance from the pivot."""
    n_weights = 13  # the number of weights, A to M, each from 1 to 13

    model = Model()

    # w[name] is the weight with that letter.
    w = {name: model.intvar(1, n_weights, name=name) for name in "abcdefghijklm"}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[name] for name in "abcdefghijklm")

    # Every weight is different.
    model.all_different(list(w.values())).post()

    # Posts a balance between the two sides of a bar. Each side is a list of
    # (distance, weight) pairs, and the total of distance times weight must match.
    def balance(left, right):
        weights = [weight for _, weight in left] + [weight for _, weight in right]
        distances = [distance for distance, _ in left] + [-distance for distance, _ in right]
        model.scalar(weights, distances, "=", 0).post()

    # Bottom left bar: A at distance 4 balances B at distance 1.
    balance([(4, a)], [(1, b)])
    # Bottom right bar: C at distance 5 balances D at distance 1.
    balance([(5, c)], [(1, d)])
    # Bar holding E and F: E at distance 3 balances F at distance 2.
    balance([(3, e)], [(2, f)])
    # Bar holding G: G at distance 3 balances the C-D bar, which weighs C + D, at distance 2.
    balance([(3, g)], [(2, c), (2, d)])
    # Bar holding J and K: the A-B bar (weight A + B) at distance 3 and J at distance 2
    # balance K at distance 1 and the G bar (weight G + C + D) at distance 2.
    balance([(3, a), (3, b), (2, j)], [(1, k), (2, g), (2, c), (2, d)])
    # Bar holding H and I: H at distance 3 balances the E-F bar (weight E + F) at
    # distance 2 and I at distance 3.
    balance([(3, h)], [(2, e), (2, f), (3, i)])
    # Bar holding L and M: the H-I bar with the E-F bar (total weight H + I + E + F) at
    # distance 1 balances L at distance 1 and M at distance 4.
    balance([(1, h), (1, i), (1, e), (1, f)], [(1, l), (4, m)])
    # Top bar: the side with L, M, H, I, E and F at distance 4 balances the side with
    # J, K, G, A, B, C and D at distance 3.
    balance([(4, l), (4, m), (4, h), (4, i), (4, e), (4, f)],
            [(3, j), (3, k), (3, g), (3, a), (3, b), (3, c), (3, d)])

    return model, w, None


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
