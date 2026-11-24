% broken_weights: a MiniZinc model from DCP Rosetta.
%
% A merchant had a measuring weight that broke into a number of pieces as the result of a fall. When the
% pieces were subsequently weighed, the weight of each piece was a whole number of pounds, and the pieces
% could be used to weigh every integral weight between 1 and the total weight. Find the weights of the
% pieces. The merchant weighs on a balance scale: a piece may go on the object's pan, on the other pan,
% or be left off, so for example a 1-pound and a 4-pound piece weigh a 3-pound object.
%
% Save this file as model.mzn. Download `broken_weights.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py broken_weights.json
%   minizinc model.mzn broken_weights_1.json

int: m;                                          % the total weight, in pounds
int: n;                                          % the number of pieces

set of int: Pieces = 1..n;                       % the pieces
set of int: Pounds = 1..m;                       % the whole weights to be weighed
set of int: Placements = 0..pow(3, n) - 1;       % a placement sets each piece to object's pan (-1), off (0) or other pan (1), by base-3 digits

array[Pieces] of var Pounds: weights;            % weights[j]: the weight of piece j, in pounds

% the pieces together weigh the total weight
constraint sum(weights) = m;

% balance[p]: weight on the other pan minus weight on the object's pan in placement p
array[Placements] of var -m..m: balance;
constraint forall(p in Placements)
    (balance[p] = sum(j in Pieces)(((p div pow(3, j-1)) mod 3 - 1) * weights[j]));

% every whole weight from 1 to the total can be weighed by some placement
constraint forall(i in Pounds)(exists(p in Placements)(balance[p] = i));

solve satisfy;
output ["{\"weights\": ", showJSON(weights), "}"];
