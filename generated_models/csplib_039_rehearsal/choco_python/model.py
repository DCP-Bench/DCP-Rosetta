# csplib_039_rehearsal: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from pychoco.model import Model


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[j]: the length of piece j
    rehearsal = instance["rehearsal"]    # rehearsal[p][j] is 1 when player p plays in piece j

    model = Model()

    # rehearsal_order[i] is the piece rehearsed in slot i
    rehearsal_order = [model.intvar(0, n_pieces - 1, name=f"rehearsal_order_{i}")
                       for i in range(n_pieces)]
    # arrival[p] is the first slot in which player p is present, departure[p] the last
    arrival = [model.intvar(0, n_pieces - 1, name=f"arrival_{p}") for p in range(n_players)]
    departure = [model.intvar(0, n_pieces - 1, name=f"departure_{p}") for p in range(n_players)]

    # Each piece is rehearsed once, so the order is a permutation of the pieces.
    model.all_different(rehearsal_order).post()

    # slot_duration[i] is the length of the piece rehearsed in slot i
    slot_duration = [model.intvar(min(duration), max(duration), name=f"slot_duration_{i}")
                     for i in range(n_pieces)]
    for i in range(n_pieces):
        model.element(slot_duration[i], duration, rehearsal_order[i]).post()

    # waiting_times holds the time each player waits in each slot
    waiting_times = []
    for p in range(n_players):
        for i in range(n_pieces):
            # playing is true when player p plays in the piece rehearsed in slot i
            playing = model.boolvar(name=f"playing_{p}_{i}")
            model.element(playing, rehearsal[p], rehearsal_order[i]).post()

            # arrived is true when slot i is not before the arrival of player p
            arrived = model.arithm(arrival[p], "<=", i).reify()
            # not_yet_gone is true when slot i is not after the departure of player p
            not_yet_gone = model.arithm(departure[p], ">=", i).reify()
            # present is true when player p is in the rehearsal room in slot i
            present = model.sum([arrived, not_yet_gone], "=", 2).reify()

            # A player who plays in a slot is present in it.
            model.arithm(playing, "<=", present).post()

            # waiting is true when player p is present in slot i but not playing.
            waiting = model.intvar(0, 1, name=f"waiting_{p}_{i}")
            model.arithm(present, "-", playing, "=", waiting).post()

            # waiting_time is the length of slot i when player p waits in it, and 0 otherwise.
            waiting_time = model.intvar(0, max(duration), name=f"waiting_time_{p}_{i}")
            model.times(slot_duration[i], waiting, waiting_time).post()
            waiting_times.append(waiting_time)

    # total_waiting is the total time players are present but not playing.
    total_waiting = model.intvar(0, n_players * sum(duration), name="total_waiting")
    model.sum(waiting_times, "=", total_waiting).post()

    # Minimise the total waiting time.
    return model, {"rehearsal_order": rehearsal_order}, {"objective": total_waiting, "maximize": False}


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
