% csplib_067_quasigroup_completion: a MiniZinc model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m: an m x m multiplication table in which each element
% from 1 to m occurs exactly once in every row and every column. Complete a partially filled quasigroup,
% given as a grid in which 0 marks an empty cell.
%
% Save this file as model.mzn. Download `csplib_067_quasigroup_completion.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_067_quasigroup_completion.json
%   minizinc model.mzn csplib_067_quasigroup_completion_1.json

include "globals.mzn";

int: N;                                          % the order m of the quasigroup
array[int, int] of int: start;                   % start[i,j]: the given value of cell (i,j), 0 if empty

set of int: Rows = 1..N;                         % the rows
set of int: Cols = 1..N;                         % the columns
set of int: Values = 1..N;                       % the values 1 to m

% puzzle[i,j]: the value of cell (i,j)
array[Rows, Cols] of var Values: puzzle;

% the given cells keep their values
constraint forall(i in Rows, j in Cols where start[i, j] != 0)(puzzle[i, j] = start[i, j]);

% each row contains each value exactly once
constraint forall(i in Rows)(all_different([puzzle[i, j] | j in Cols]));

% each column contains each value exactly once
constraint forall(j in Cols)(all_different([puzzle[i, j] | i in Rows]));

solve satisfy;
output ["{\"puzzle\": ", showJSON(puzzle), "}"];
