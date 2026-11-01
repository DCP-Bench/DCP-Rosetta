# csplib_012_nonogram: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from pychoco.model import Model
from pychoco.objects.automaton.finite_automaton import FiniteAutomaton


def line_automaton(clue):
    """Automaton accepting exactly the lines of squares (1 = shaded, 0 = unshaded) whose shaded
    blocks have the lengths in clue, in order. Blocks are separated by at least one unshaded
    square, and the line may start and end with any number of unshaded squares."""
    # steps of the automaton, as (state, shaded or not, next state)
    steps = []
    n_states = 0  # how much of the clue has been read
    for block_length in clue:
        if block_length == 0:  # zeros in a clue are padding
            continue
        steps.append((n_states, 0, n_states))  # unshaded squares before this block
        for _ in range(block_length):
            steps.append((n_states, 1, n_states + 1))  # one more shaded square of the block
            n_states += 1
        steps.append((n_states, 0, n_states + 1))  # the unshaded square after this block
        n_states += 1
    steps.append((n_states, 0, n_states))  # unshaded squares after the last block
    # The line may end right after the last block, or after the unshaded squares that follow it.
    final_states = [state for state in (n_states - 1, n_states) if state >= 0]

    automaton = FiniteAutomaton()
    states = [automaton.add_state() for _ in range(n_states + 1)]
    automaton.set_initial_state(states[0])
    for state in final_states:
        automaton.set_final(states[state])
    for source, symbol, target in steps:
        automaton.add_transition(states[source], states[target], symbol)
    return automaton


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive
    shaded squares have the lengths given by its clue, in order, with at least one
    unshaded square between blocks."""
    row_rules = instance["row_rules"]  # row_rules[r]: the blocks of row r, in order, padded with zeros
    col_rules = instance["col_rules"]  # col_rules[c]: the blocks of column c, in order, padded with zeros
    n_rows, n_cols = len(row_rules), len(col_rules)  # the number of rows and columns

    model = Model()

    # board[r][c] is 1 when the square in row r and column c is shaded, 0 when it is not
    board = [[model.intvar(0, 1, name=f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    # Each row shows the shaded blocks its clue lists, in that order.
    for r, clue in enumerate(row_rules):
        model.regular(board[r], line_automaton(clue)).post()

    # Each column shows the shaded blocks its clue lists, in that order.
    for c, clue in enumerate(col_rules):
        model.regular([board[r][c] for r in range(n_rows)], line_automaton(clue)).post()

    return model, {"board": board}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
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
