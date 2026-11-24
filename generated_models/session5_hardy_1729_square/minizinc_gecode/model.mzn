% session5_hardy_1729_square: a MiniZinc model from DCP Rosetta.
%
% Find a combination of 4 different numbers between 1 and 100, such that the sum of the squares of the two
% first numbers is equal to the sum of the squares of the other two numbers, i.e. a^2 + b^2 = c^2 + d^2 for
% a, b, c and d between 1 and 100, all different.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: min_number = 1;                              % the smallest number allowed
int: max_number = 100;                            % the largest number allowed

var min_number..max_number: a;
var min_number..max_number: b;
var min_number..max_number: c;
var min_number..max_number: d;

% the sum of the squares of a and b equals the sum of the squares of c and d
constraint a * a + b * b = c * c + d * d;

% the four numbers are all different
constraint all_different([a, b, c, d]);

solve satisfy;
output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), ", \"c\": ", showJSON(c), ", \"d\": ", showJSON(d), "}"];
