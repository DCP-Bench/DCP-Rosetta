from hermax.model import Model


def build(instance):
    nums = instance["nums"]
    count = instance["m"]          # how many elements must be selected
    n = len(nums)

    m = Model()
    # sel[i] is true when element i is part of the selected group.
    sel = m.bool_vector("sel", n)

    # Select a number of elements: exactly `count` of them.
    m &= (sum(sel[i] for i in range(n)) == count)

    # The selected elements sum to zero.
    m &= (sum(nums[i] * sel[i] for i in range(n)) == 0)

    return m, {"indices": sel}
