# csplib_039_rehearsal: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from hermax.model import Model


def create_model(instance):
    """Order the pieces of a concert for rehearsal so that the total time the players
    spend present but not playing is as small as possible. A player arrives just before
    the first piece they play in and leaves just after the last one."""
    num_pieces = instance["num_pieces"]    # the number of pieces in the concert
    num_players = instance["num_players"]  # the number of players in the orchestra
    duration = instance["duration"]        # duration[j]: the length of piece j
    rehearsal = instance["rehearsal"]      # rehearsal[p][j] = 1 when player p plays in piece j
    total = sum(duration)                  # the length of the rehearsal when every piece is played once

    m = Model()

    # at[s][j] is true when piece j is rehearsed in slot s
    at = m.bool_matrix("at", num_pieces, num_pieces)
    # rehearsal_order[s] is the piece rehearsed in slot s (the declared output)
    rehearsal_order = m.int_vector("rehearsal_order", num_pieces, 0, num_pieces - 1)
    # start[s] is the time at which slot s begins; start[num_pieces] is the time the rehearsal ends
    start = m.int_vector("start", num_pieces + 1, 0, total)

    # Each slot rehearses exactly one piece, and each piece is rehearsed in exactly one slot.
    for s in range(num_pieces):
        m &= at.row(s).exactly_one()
    for j in range(num_pieces):
        m &= at.col(j).exactly_one()

    # rehearsal_order[s] is the piece that at puts in slot s.
    for s in range(num_pieces):
        for j in range(num_pieces):
            m &= (~at[s][j] | (rehearsal_order[s] == j))

    # The rehearsal starts at time 0, and each slot lasts as long as the piece rehearsed in it.
    m &= (start[0] == 0)
    for s in range(num_pieces):
        m &= (start[s + 1] == start[s] + sum(duration[j] * at[s][j] for j in range(num_pieces)))

    for p in range(num_players):
        pieces = [j for j in range(num_pieces) if rehearsal[p][j]]  # the pieces player p plays in
        if not pieces:
            continue  # a player who plays nothing never attends, so never waits

        # arrive is the time player p arrives, leave is the time player p leaves
        arrive = m.int(f"arrive_{p}", 0, total)
        leave = m.int(f"leave_{p}", 0, total)
        # The player has arrived by the start of every slot in which they play,
        # and stays until the end of every such slot.
        for s in range(num_pieces):
            for j in pieces:
                m &= (arrive <= start[s]).only_if(at[s][j])
                m &= (leave >= start[s + 1]).only_if(at[s][j])

        # Objective, for player p: the time present (from arrival to leaving) less the time
        # spent playing. Minimising the sum over players minimises the total waiting time.
        m.obj += leave - arrive - sum(duration[j] for j in pieces)

    return m, {"rehearsal_order": rehearsal_order}


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
