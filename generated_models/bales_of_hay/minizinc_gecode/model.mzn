% bales_of_hay: a MiniZinc model from DCP Rosetta.
%
% You have a number of bales of hay. Instead of being weighed individually, they were weighed in all
% possible combinations of two. The weights of each of these combinations were written down and arranged
% in numerical order, without keeping track of which weight matched which pair of bales. The weights are
% given in a list. Find the weight of each bale.
%
% Save this file as model.mzn. Download `bales_of_hay.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py bales_of_hay.json
%   minizinc model.mzn bales_of_hay_1.json

include "globals.mzn";

int: n;                                              % the number of bales
array[int] of int: weights;                          % the weights of the pairs of bales, in any order

set of int: Bales = 1..n;                            % one index per bale
set of int: Weights = index_set(weights);            % one index per pair weight

% assumption: a bale's weight is non-negative, so none weighs more than the heaviest pair
array[Bales] of var 0..max(weights): bales;

% the weight of every pair of bales, one entry per pair
array[int] of var int: pairs = [bales[i] + bales[j] | i, j in Bales where i < j];

% the pair weights are exactly the given weights, each occurring as often as it is given
constraint forall(k in Weights)(count(pairs, weights[k]) = count(weights, weights[k]));

% the bales are listed lightest first (their order is free, so this only picks one of each permutation)
constraint forall(i in 1..n-1)(bales[i] <= bales[i+1]);

% implied constraint (redundant, added for propagation): the two lightest bales make the lightest pair
constraint bales[1] + bales[2] = min(weights);

% implied constraint (redundant, added for propagation): the two heaviest bales make the heaviest pair
constraint bales[n-1] + bales[n] = max(weights);

% implied constraint (redundant, added for propagation): each bale appears in n-1 pairs, so the pair weights add up to (n-1) times the total weight
constraint sum(weights) = (n-1) * sum(bales);

solve satisfy;
output ["{\"bales\": ", showJSON(bales), "}"];
