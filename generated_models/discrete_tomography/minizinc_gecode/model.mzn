% discrete_tomography: a MiniZinc model from DCP Rosetta.
%
% A matrix which contains zeroes and ones gets "x-rayed" vertically and horizontally, giving the total
% number of ones in each row and each column. Reconstruct the contents of the matrix from this
% information.
%
% Save this file as model.mzn. Download `discrete_tomography.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py discrete_tomography.json
%   minizinc model.mzn discrete_tomography_1.json

array[int] of int: row_sums;                     % row_sums[i]: the number of ones in row i
array[int] of int: col_sums;                     % col_sums[j]: the number of ones in column j

set of int: Rows = index_set(row_sums);          % the rows of the matrix
set of int: Cols = index_set(col_sums);          % the columns of the matrix

% matrix[i,j]: the entry in row i and column j, 0 or 1
array[Rows, Cols] of var 0..1: matrix;

% the number of ones in each row is the given row sum
constraint forall(i in Rows)(sum(j in Cols)(matrix[i, j]) = row_sums[i]);

% the number of ones in each column is the given column sum
constraint forall(j in Cols)(sum(i in Rows)(matrix[i, j]) = col_sums[j]);

solve satisfy;
output ["{\"matrix\": ", showJSON(matrix), "}"];
