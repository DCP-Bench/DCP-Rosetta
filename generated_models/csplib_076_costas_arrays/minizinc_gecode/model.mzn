% csplib_076_costas_arrays: a MiniZinc model from DCP Rosetta.
%
% A Costas array is a pattern of n marks on an n x n grid, one mark per row and one per column, in
% which the n(n-1)/2 vectors between pairs of marks are all different. Find a Costas array of size n.
%
% Save this file as model.mzn. Download `csplib_076_costas_arrays.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_076_costas_arrays.json
%   minizinc model.mzn csplib_076_costas_arrays_1.json

include "globals.mzn";

int: n;                                          % the size of the grid, and the number of marks

set of int: Positions = 1..n;                    % the rows (and the columns)

% costas[i]: the column of the mark in row i
array[Positions] of var Positions: costas;

% each column of the grid holds exactly one mark (one mark per row is given by the indexing)
constraint all_different(costas);

% for each vector length l, the differences costas[i+l] - costas[i] are all different
constraint forall(l in 1..n-1)(
    all_different([costas[i + l] - costas[i] | i in 1..n-l])
);

solve satisfy;
output ["{\"costas\": ", showJSON(costas), "}"];
