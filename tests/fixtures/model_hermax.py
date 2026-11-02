from hermax.model import Model


def create_model(instance):
    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    if instance["optimize"]:
        m &= (x + y >= n)
        m.obj += (x + y)
    else:
        m &= (x + y == n)
    return m, {"x": x, "y": y}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
