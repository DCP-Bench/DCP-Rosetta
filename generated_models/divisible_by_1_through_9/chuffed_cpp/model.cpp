// Divisible by 1 through 9: find a ten-digit number that uses each digit 0 to 9 exactly
// once and where, for every n, the number formed by its first n digits is divisible by n.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // The statement fixes all the data (ten digits, divisors 1 to 10), so the instance has
  // no fields.
  const int n_digits = 10;

  // digits[i]: the digit at position i of the number, read from left to right
  vec<IntVar*> digits;
  createVars(digits, n_digits, 0, 9);

  // Each of the digits 0 to 9 is used exactly once.
  all_different(digits);

  // The number formed by the first n digits is divisible by n: it is n times a whole
  // number, the quotient.
  // That number is the sum of digits[j] * 10^(n-1-j), which from n = 9 on can exceed
  // Chuffed's domain bound of 500,000,000. Replacing each place value 10^(n-1-j) by its
  // remainder modulo n leaves the remainder of the sum modulo n unchanged and keeps the
  // sum below 1000. Chuffed has no working modulo constraint (int_mod aborts), so the
  // divisibility is the linear equation sum - n * quotient = 0.
  for (int n = 1; n <= n_digits; ++n) {
    vec<int> coefficients;
    vec<IntVar*> terms;
    int largest_sum = 0;
    for (int j = 0; j < n; ++j) {
      int place_value = 1 % n;  // 10^(n-1-j) mod n, built up one factor of 10 at a time
      for (int k = 0; k < n - 1 - j; ++k) place_value = place_value * 10 % n;
      coefficients.push(place_value);
      terms.push(digits[j]);
      largest_sum += 9 * place_value;
    }
    IntVar* quotient = newIntVar(0, largest_sum / n);
    coefficients.push(-n);
    terms.push(quotient);
    int_linear(coefficients, terms, IRT_EQ, 0);
  }

  // Search over the digits.
  branch(digits, VAR_INORDER, VAL_MIN);

  json digit_outputs = json::array();
  for (int i = 0; i < n_digits; ++i) digit_outputs.push_back(dcp::out(digits[i]));
  outputs = {{"digits", digit_outputs}};
}
