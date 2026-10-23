from hermax.model import Model


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    m = Model()

    # Boolean variables: True means add (+), False means subtract (-)
    signs = m.bool_vector("signs", n)

    # Result array: result[i] = arr[i] if signs[i] else -arr[i]
    result = []
    for i in range(n):
        # Create a variable for result[i] with range [-arr[i], arr[i]]
        result_i = m.int(f"result_{i}", -arr[i], arr[i])
        # If signs[i] is True, result_i = arr[i]; else result_i = -arr[i]
        # This can be expressed as: result_i == (2 * signs[i] - 1) * arr[i]
        # Or: result_i = arr[i] when signs[i]=True, -arr[i] when signs[i]=False
        # result_i = 2*signs[i]*arr[i] - arr[i]
        m &= (result_i == arr[i] * (2 * signs[i] - 1))
        result.append(result_i)

    # Sum should equal total
    m &= (sum(result) == total)

    return m, {"result": result}
