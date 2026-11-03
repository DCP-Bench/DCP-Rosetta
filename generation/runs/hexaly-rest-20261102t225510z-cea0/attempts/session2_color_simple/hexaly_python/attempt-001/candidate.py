"""Map colouring: colour the countries so that neighbours differ, using as few colours as possible."""
import hexaly.optimizer as hx


def build(instance):
    edges = instance["graph"]  # pairs of neighbouring countries, numbered from 1
    countries = max(max(edge) for edge in edges)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # colors[i] is the colour (1, 2, ...) of country i; no more colours than countries are needed
    colors = [model.int(1, countries) for _ in range(countries)]

    # Neighbouring countries have different colours
    for a, b in edges:
        model.constraint(colors[a - 1] != colors[b - 1])

    # Minimise the number of colours: the colours used are 1, 2, ... up to the largest
    model.minimize(model.max(colors))
    return optimizer, {"colors": colors}
