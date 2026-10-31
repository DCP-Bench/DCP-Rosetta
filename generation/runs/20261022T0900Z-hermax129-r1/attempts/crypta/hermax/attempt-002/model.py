from hermax.model import Model


def build(instance):
    """
    Cryptarithmetic puzzle: solve the addition using carry-based constraint

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

    # All different constraint: each letter gets a unique digit
    m &= digit_vector.all_different()

    # First letters cannot be 0 (B, D, G are leading digits)
    m &= (digits['B'] >= 1)
    m &= (digits['D'] >= 1)
    m &= (digits['G'] >= 1)

    # Define the numbers as lists of digit characters (left to right)
    num1_chars = ['B', 'A', 'I', 'J', 'J', 'A', 'J', 'I', 'I', 'A', 'H', 'F', 'C', 'F', 'E', 'B', 'B', 'J', 'E', 'A']
    num2_chars = ['D', 'H', 'F', 'G', 'A', 'B', 'C', 'D', 'I', 'D', 'B', 'I', 'F', 'F', 'A', 'G', 'F', 'E', 'J', 'E']
    result_chars = ['G', 'J', 'E', 'G', 'A', 'C', 'D', 'D', 'H', 'F', 'A', 'F', 'J', 'B', 'F', 'I', 'H', 'E', 'E', 'F']

    n = 20  # Number of digits

    # Create carry variables: carries[i] is the carry from position i to i+1 (going right to left)
    carries = m.int_vector("carry", n + 1, 0, 1)
    m &= (carries[n] == 0)  # No carry out of the most significant digit

    # Add digit by digit from right to left
    for i in range(n):
        # Position from the right
        pos = n - 1 - i

        d1 = digits[num1_chars[pos]]
        d2 = digits[num2_chars[pos]]
        dr = digits[result_chars[pos]]
        c_in = carries[i]
        c_out = carries[i + 1]

        # Constraint: d1 + d2 + c_in = dr + 10 * c_out
        m &= (d1 + d2 + c_in == dr + 10 * c_out)

    return m, {l: digits[l] for l in letters}
