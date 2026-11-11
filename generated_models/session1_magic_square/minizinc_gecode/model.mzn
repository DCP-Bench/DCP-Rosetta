% session1_magic_square: a MiniZinc model from DCP Rosetta.
%
% A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 and the
% sum of the integers in each row, column and diagonal is equal. Find a magic square for a given size n, knowing that the sum
% of integers of each row, column and diagonal has to be equal to n(n^2+ 1)/2 (integer).
%
% Save this file as model.mzn. Download `session1_magic_square.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session1_magic_square.json
%   minizinc model.mzn session1_magic_square_1.json

include "globals.mzn";

int: n;                                              % the size of the square

set of int: Cells = 1..n;                            % the rows and the columns
int: magic_sum = n * (n * n + 1) div 2;              % the sum of each row, column and diagonal

array[Cells, Cells] of var 1..n * n: square;         % square[i,j]: the integer in row i, column j

% each cell contains a different integer
constraint all_different([square[i, j] | i, j in Cells]);

% the sum of the integers in each row is the magic sum
constraint forall(i in Cells)(sum(j in Cells)(square[i, j]) = magic_sum);

% the sum of the integers in each column is the magic sum
constraint forall(j in Cells)(sum(i in Cells)(square[i, j]) = magic_sum);

% the sum of the integers on the main diagonal is the magic sum
constraint sum(i in Cells)(square[i, i]) = magic_sum;

% the sum of the integers on the other diagonal is the magic sum
constraint sum(i in Cells)(square[i, n + 1 - i]) = magic_sum;

solve satisfy;
output ["{\"square\": ", showJSON(square), "}"];
