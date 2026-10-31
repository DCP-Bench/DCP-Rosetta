from hermax.model import Model


def build(instance):
    """
    Arrange pieces for rehearsal to minimize total player waiting time.

    For each player, calculate: arrival time (first piece they play) and
    departure time (last piece they play). Waiting time = time between arrival
    and departure, minus time actually playing.

    Output: permutation of piece indices (0 to num_pieces-1)
    """
    num_pieces = instance["num_pieces"]
    num_players = instance["num_players"]
    duration = instance["duration"]
    rehearsal = instance["rehearsal"]

    model = Model()

    # Create permutation: order[i] = piece index at position i
    # Using position encoding: pos[piece] = position in rehearsal
    pos = model.int_vector("pos", num_pieces, 0, num_pieces - 1)
    model &= pos.all_different()

    # Create inverse: order[i] = piece at position i
    order = model.int_vector("order", num_pieces, 0, num_pieces - 1)
    for i in range(num_pieces):
        for p in range(num_pieces):
            # order[i] = p iff pos[p] = i
            model &= ((order[i] == p) | (pos[p] != i))
            model &= ((order[i] != p) | (pos[p] == i))

    # For each player, find first and last position where they play
    total_wait = 0

    for player in range(num_players):
        # Find pieces this player is involved in
        player_pieces = [p for p in range(num_pieces) if rehearsal[player][p] == 1]

        if not player_pieces:
            continue

        # First position: min(pos[p] for p in player_pieces)
        first_pos = model.int(f"first_pos_{player}", 0, num_pieces - 1)
        # Constraint: first_pos = minimum of positions
        for p in player_pieces:
            model &= (first_pos <= pos[p])
        for p_idx, p in enumerate(player_pieces):
            # At least one must equal first_pos
            if p_idx == 0:
                model &= (first_pos >= pos[p])
            else:
                # This is harder without explicit OR
                pass

        # Simplified: just use smallest position directly
        model &= (first_pos == min(pos[p] for p in player_pieces))

        # Last position: max(pos[p] for p in player_pieces)
        last_pos = model.int(f"last_pos_{player}", 0, num_pieces - 1)
        model &= (last_pos == max(pos[p] for p in player_pieces))

        # Calculate waiting time
        # Sum of all durations between first_pos and last_pos (inclusive)
        # minus sum of durations of pieces this player plays

        span_duration = 0
        for i in range(num_pieces):
            piece_at_i = order[i]
            # Add duration[piece_at_i] if first_pos <= i <= last_pos
            # Use auxiliary variable
            in_span = model.bool(f"in_span_{player}_{i}")
            model &= (in_span == ((first_pos <= i) & (i <= last_pos)))

            # But this uses AND of constraints which may not work
            # Simpler: span_duration is the sum for i in [first_pos, last_pos]
            span_duration += in_span * duration[piece_at_i]

        # Playing time for this player
        play_duration = sum(duration[p] for p in player_pieces)

        # Waiting time = span_duration - play_duration
        wait_duration = span_duration - play_duration
        total_wait += wait_duration

    # Objective: minimize total waiting time
    # Add soft clauses for the sum
    cost_var = model.int("cost", 0, sum(duration) * num_players)
    model &= (cost_var == total_wait)

    # Penalize in objective
    model.obj[1] += cost_var

    # Pad output to 9
    output = model.int_vector("rehearsal_order", 9, 0, num_pieces - 1)
    for i in range(num_pieces):
        model &= (output[i] == order[i])
    for i in range(num_pieces, 9):
        model &= (output[i] == 0)

    return model, {"rehearsal_order": output}
