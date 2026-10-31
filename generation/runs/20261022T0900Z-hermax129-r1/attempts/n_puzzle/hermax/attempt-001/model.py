from hermax.model import Model


def build(instance):
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    steps = instance["N_STEPS"]
    n = len(start)
    cells = n * n

    def neighbours(p):
        r, c = divmod(p, n)
        out = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n:
                out.append(rr * n + cc)
        return out

    m = Model()
    # state[t][p] is the tile at flat position p at step t; 0 is the blank.
    state = []
    for t in range(steps):
        vec = m.int_vector(f"state{t}", cells, 0, cells - 1)
        m &= vec.all_different()
        state.append(vec)

    # The first and last states are the given start and end boards.
    for r in range(n):
        for c in range(n):
            p = r * n + c
            m &= (state[0][p] == start[r][c])
            m &= (state[steps - 1][p] == end[r][c])

    # Each step is one move: the blank slides to an adjacent cell and the
    # tile there slides into the old blank position. Other tiles stay put.
    for t in range(steps - 1):
        moves = []
        for p in range(cells):
            for q in neighbours(p):
                mv = m.bool()
                moves.append(mv)
                # The blank is at p now and at q after the move.
                m &= (state[t][p] == 0).only_if(mv)
                m &= (state[t + 1][q] == 0).only_if(mv)
                # The tile from q now sits at p.
                m &= (state[t + 1][p] == state[t][q]).only_if(mv)
                # Every other position is unchanged.
                for r in range(cells):
                    if r != p and r != q:
                        m &= (state[t + 1][r] == state[t][r]).only_if(mv)
        # Exactly one move per step.
        m &= (sum(moves) == 1)

    result = [
        [[state[t][r * n + c] for c in range(n)] for r in range(n)]
        for t in range(steps)
    ]
    return m, {"steps": result}
