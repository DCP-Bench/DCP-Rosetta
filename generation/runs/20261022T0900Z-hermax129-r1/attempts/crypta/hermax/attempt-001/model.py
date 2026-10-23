from hermax.model import Model


def build(instance):
    """
    Cryptarithmetic puzzle: solve the addition

      B A I J J A J I I A H F C F E B B J E A
    +  D H F G A B C D I D B I F F A G F E J E
    = G J E G A C D D H F A F J B F I H E E F

    Fixed constants: 10 distinct letters (A-J) assigned to 0-9
    """
    m = Model()

    # Each letter gets a digit 0-9
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    digit_vector = m.int_vector("digit", 10, 0, 9)
    digits = {letters[i]: digit_vector[i] for i in range(10)}

    # All different constraint
    m &= digit_vector.all_different()

    # First letters cannot be 0 (B, D, G are leading digits)
    m &= (digits['B'] >= 1)
    m &= (digits['D'] >= 1)
    m &= (digits['G'] >= 1)

    # Define the digit sequences for each number
    num1_str = "BAIJJAJIIAHFCFEBBJEA"
    num2_str = "DHFGABCDIDBIFFAGFEJE"
    result_str = "GJEGACDDHFAFJBFIHEEEF"
    n = 20

    # Convert digit sequences to numbers
    # Using decomposition to avoid overflow: sum(d[i] * 10^i) by grouping in chunks
    # We'll express each number as a sum of base-10 terms

    num1 = sum(digits[num1_str[n - 1 - i]] * (10 ** i) for i in range(n))
    num2 = sum(digits[num2_str[n - 1 - i]] * (10 ** i) for i in range(n))
    result = sum(digits[result_str[n - 1 - i]] * (10 ** i) for i in range(n))

    # Addition constraint
    m &= (num1 + num2 == result)

    return m, {l: digits[l] for l in letters}
