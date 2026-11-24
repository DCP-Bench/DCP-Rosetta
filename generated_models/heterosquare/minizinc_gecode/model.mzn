% heterosquare: a MiniZinc model from DCP Rosetta.
%
% A heterosquare of order n is an n by n square whose elements are distinct integers from 1 to n^2
% such that the sums of the rows, columns and diagonals are all different from each other.
%
% Save this file as model.mzn. Download `heterosquare.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py heterosquare.json
%   minizinc model.mzn heterosquare_1.json

include "globals.mzn";

int: n;                                          % the order of the square

set of int: Rows = 1..n;                         % row and column indices
set of int: Cells = 1..n*n;                      % the values to place: 1..n^2

array[Rows, Rows] of var Cells: x;               % x[i,j]: the element in row i, column j
set of int: Sums = 1..n*n*n;                     % the possible sums: at most n entries, each at most n^2
array[Rows] of var Sums: row_sums;           % row_sums[i]: sum of row i
array[Rows] of var Sums: col_sums;           % col_sums[j]: sum of column j
var Sums: diag1;                             % sum of the main diagonal
var Sums: diag2;                             % sum of the anti-diagonal

% the elements of the square are distinct
constraint all_different([x[i, j] | i in Rows, j in Rows]);

% row_sums and col_sums are the sums of their rows and columns
constraint forall(i in Rows)(row_sums[i] = sum(j in Rows)(x[i, j]));
constraint forall(j in Rows)(col_sums[j] = sum(i in Rows)(x[i, j]));
constraint diag1 = sum(i in Rows)(x[i, i]);
constraint diag2 = sum(i in Rows)(x[i, n + 1 - i]);

% the sums of the rows, columns and diagonals are all different
constraint all_different(row_sums ++ col_sums ++ [diag1, diag2]);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
