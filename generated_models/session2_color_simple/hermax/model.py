# session2_color_simple: a hermax (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install hermax`):
#   python session2_color_simple.py session2_color_simple.json

from hermax.model import Model


def create_model(instance):
    """Colour the countries so that two neighbouring countries never share a colour,
    using as few colours as possible. Colours are integers starting from 1."""
    graph = instance["graph"]  # graph[k] = [a, b]: countries a and b (numbered from 1) are neighbours
    # Every country appears in at least one border (true for the six listed countries), so the largest number in the edge list is the count.
    num_nodes = max(max(edge) for edge in graph)

    m = Model()
    # colors[i] is the colour of country i + 1, an integer from 1 to num_nodes
    colors = m.int_vector("colors", num_nodes, 1, num_nodes)

    # Neighbouring countries get different colours: one constraint per border.
    for left, right in graph:
        m &= (colors[left - 1] != colors[right - 1])

    # Minimise the number of colours used. At the optimum the colours used are 1..k,
    # so the largest colour number is the number of colours used.
    m.obj += m.max(colors, name="used")

    return m, {"colors": colors}


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
