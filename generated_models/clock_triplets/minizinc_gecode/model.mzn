% clock_triplets: a MiniZinc model from DCP Rosetta.
%
% Rearrange the numbers on the face of a clock (1 to 12) so that no triplet of adjacent numbers has a sum
% higher than 21, which is the smallest value that the highest sum of a triplet can have.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: max_triplet_sum = 21;                  % the largest allowed sum of three adjacent numbers
int: hours = 12;                             % the number of positions on the clock face

% x[i]: the number at position i of the clock face, positions wrap around
array[1..hours] of var 1..hours: x;

% the numbers on the face are 1 to 12, each used once
constraint all_different(x);

% no three adjacent numbers on the face sum to more than the largest allowed sum
constraint forall(i in 1..hours)(
    x[i] + x[i mod hours + 1] + x[(i + 1) mod hours + 1] <= max_triplet_sum
);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
