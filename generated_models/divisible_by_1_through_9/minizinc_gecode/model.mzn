% divisible_by_1_through_9: a MiniZinc model from DCP Rosetta.
%
% Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where the number formed by
% the first n digits of the number is divisible by n. Read the digits from left to right: in the number
% abcd, the number a is divisible by 1, the number ab by 2, the number abc by 3, and the entire number
% abcd by 4.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

set of int: Digits = 1..10;                      % the positions of the digits, from left to right

% digit[p]: the digit at position p
array[Digits] of var 0..9: digit;

% each of the digits 0 to 9 is used exactly once
constraint all_different(digit);

% the number is a 10 digit number, so its leading digit is not 0
constraint digit[1] != 0;

% the number formed by the first n digits is divisible by n, for n from 1 to 9
constraint forall(n in 1..9)(
    sum(p in 1..n)(digit[p] * pow(10, n - p)) mod n = 0
);

% the number formed by the first 10 digits is divisible by 10, so its last digit is 0
constraint digit[10] = 0;

solve satisfy;
output ["{\"digits\": ", showJSON(digit), "}"];
