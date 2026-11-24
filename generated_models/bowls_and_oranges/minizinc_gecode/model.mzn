% bowls_and_oranges: a MiniZinc model from DCP Rosetta.
%
% You have a number of bowls, numbered from 1 and all placed in a line at exact intervals of 1 meter.
% You also have a number of oranges. You wish to place all the oranges in the bowls, no more than one
% orange in each bowl, so that there are no three oranges A, B, and C such that the distance between A
% and B is equal to the distance between B and C. Give the bowls in which the oranges are placed, in
% ascending order.
%
% Save this file as model.mzn. Download `bowls_and_oranges.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py bowls_and_oranges.json
%   minizinc model.mzn bowls_and_oranges_1.json

include "globals.mzn";

int: n;                                  % the number of bowls
int: m;                                   % the number of oranges

set of int: Bowls = 1..n;                 % the bowls, numbered from 1
set of int: Oranges = 1..m;               % the oranges

% x[k]: the bowl holding the k-th orange, in ascending order
array[Oranges] of var Bowls: x;

% no more than one orange in each bowl, and the bowls are listed in ascending order
constraint strictly_increasing(x);

% no three oranges A, B, C (in bowl order) are such that the distance from A to B equals the distance from B to C
constraint forall(i, j, k in Oranges where i < j /\ j < k)(x[j] - x[i] != x[k] - x[j]);

solve satisfy;
output ["{\"x\": ", showJSON(x), "}"];
