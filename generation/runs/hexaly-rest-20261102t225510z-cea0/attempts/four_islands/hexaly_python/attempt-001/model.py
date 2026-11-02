"""Four islands: match islands, exports and attractions to the map positions A=0, B=1 (top) and C=2, D=3 (bottom)."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    def group():
        """Four map positions, one for each of the four items of a kind, all different."""
        positions = [model.int(0, 3) for _ in range(4)]
        for a in range(4):
            for b in range(a + 1, 4):
                model.constraint(model.not_(positions[a] == positions[b]))
        return positions

    island, export, attraction = group(), group(), group()
    pwana, quero, rayou, skern = island
    alabaster, bananas, coconuts, durian = export
    hotel, rink, jai_alai, koala = attraction

    # Positions: 0 north-west, 1 north-east, 2 south-west, 3 south-east. P is due south of Q when P = Q + 2,
    # and P is due east of Q when P = Q + 1 and Q is in the west (0 or 2).
    # 1. The koala preserve island is due south of Pwana
    model.constraint(koala == pwana + 2)
    # 2. The alabaster island is due west of Quero
    model.constraint(model.or_(model.and_(alabaster == 0, quero == 1), model.and_(alabaster == 2, quero == 3)))
    # 3. The hotel island is due east of the durian island
    model.constraint(model.or_(model.and_(durian == 0, hotel == 1), model.and_(durian == 2, hotel == 3)))
    # 4. Skern and the jai alai island are joined by a north-south bridge
    model.constraint(model.abs(skern - jai_alai) == 2)
    # 5. Rayou and the banana island are joined by an east-west bridge
    model.constraint(model.or_(*[model.and_(rayou == a, bananas == b)
                                 for a, b in ((0, 1), (1, 0), (2, 3), (3, 2))]))
    # 6. The ice skating rink and jai alai islands are not joined by a bridge: they are diagonal
    model.constraint(rink + jai_alai == 3)

    return optimizer, {"island": island, "export": export, "attraction": attraction}
