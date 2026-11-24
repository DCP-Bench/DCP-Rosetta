% flip_rows_cols: a MiniZinc model from DCP Rosetta.
%
% Given an array of positive and negative numbers, you may flip the sign of any entire rows and any
% columns, as many as you like. Make every row and every column sum to a positive number (or zero),
% and choose the flips that give the smallest overall sum.
%
% Save this file as model.mzn. Download `flip_rows_cols.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py flip_rows_cols.json
%   minizinc model.mzn flip_rows_cols_1.json

array[int,int] of int: input_matrix;               % input_matrix[i,j]: the number in row i, column j
set of int: Rows = index_set_1of2(input_matrix);    % one index per row
set of int: Columns = index_set_2of2(input_matrix); % one index per column
int: max_abs = max(i in Rows, j in Columns)(abs(input_matrix[i,j])); % largest magnitude of a number

% row_signs[i]: -1 if row i is flipped, 1 otherwise
array[Rows] of var {-1, 1}: row_signs;
% col_signs[j]: -1 if column j is flipped, 1 otherwise
array[Columns] of var {-1, 1}: col_signs;

% x[i,j]: the number in row i, column j after the flips
array[Rows, Columns] of var -max_abs..max_abs: x;
constraint forall(i in Rows, j in Columns)(x[i,j] = input_matrix[i,j] * row_signs[i] * col_signs[j]);

% every row sums to a positive number or zero
constraint forall(i in Rows)(sum(j in Columns)(x[i,j]) >= 0);

% every column sums to a positive number or zero
constraint forall(j in Columns)(sum(i in Rows)(x[i,j]) >= 0);

% the overall sum of the array after the flips, to be minimised
var int: objective = sum(i in Rows, j in Columns)(x[i,j]);

solve minimize objective;

output ["{\"row_signs\": ", showJSON(row_signs), ", \"col_signs\": ", showJSON(col_signs), "}"];
