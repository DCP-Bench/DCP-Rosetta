% pythagorean_triplet: a MiniZinc model from DCP Rosetta.
%
% A Pythagorean triplet is a set of three natural numbers a, b and c for which a^2 + b^2 = c^2. The order
% of a and b does not matter. There exists exactly one Pythagorean triplet for which a + b + c = 1000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

int: total = 1000;                       % the sum a + b + c

var 1..total: a;                         % a natural number
var 1..total: b;                         % a natural number
var 1..total: c;                         % a natural number

% the order of a and b does not matter, so a is the smaller of the two
constraint a < b;

% the three numbers sum to the total
constraint a + b + c = total;

% a^2 + b^2 = c^2
constraint a * a + b * b = c * c;

solve satisfy;

output ["{\"a\": ", showJSON(a), ", \"b\": ", showJSON(b), ", \"c\": ", showJSON(c), "}"];
