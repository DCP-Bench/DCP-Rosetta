% Divisible by 1 through 9: find a ten-digit number that uses each digit 0 to 9 exactly
% once and where, for every n, the number formed by its first n digits is divisible by n.
% The statement fixes all the data (ten digits, divisors 1 to 10), so the instance has no
% fields.
include "globals.mzn";

int: n_digits = 10;

% digits[i]: the i-th digit of the number, read from left to right
array[1..n_digits] of var 0..9: digits;

% Each of the digits 0 to 9 is used exactly once.
constraint all_different(digits);

% The number formed by the first n digits is divisible by n.
% That number is the sum of digits[j] * 10^(n-j), which for n = 10 is above 2^31 - 1, the
% largest integer Gecode holds. Replacing each place value 10^(n-j) by its remainder modulo
% n leaves the remainder of the sum modulo n unchanged and keeps the sum below 1000.
constraint forall(n in 1..n_digits)(
  sum(j in 1..n)((pow(10, n - j) mod n) * digits[j]) mod n = 0
);

solve satisfy;

output ["{\"digits\": ", show(digits), "}"];
