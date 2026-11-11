% csplib_054_n_queens: a MiniZinc model from DCP Rosetta.
%
% Can n queens (of the same color) be placed on an n x n chessboard so that none of the queens can attack
% each other? A queen attacks the squares on the same row, column, or either diagonal as itself, so the
% n-queens problem is to find a set of n locations on a chessboard, no two of which are on the same row,
% column or diagonal.
%
% Save this file as model.mzn. Download `csplib_054_n_queens.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_054_n_queens.json
%   minizinc model.mzn csplib_054_n_queens_1.json

include "globals.mzn";

int: n;                                          % the size of the chessboard and the number of queens

set of int: Rows = 1..n;                         % the rows of the chessboard
set of int: Columns = 1..n;                      % the columns of the chessboard

% queens[i]: the column of the queen in row i
array[Rows] of var Columns: queens;

% no two queens are on the same column
constraint all_different(queens);

% no two queens are on the same diagonal, one way
constraint all_different([queens[i] + i | i in Rows]);

% no two queens are on the same diagonal, the other way
constraint all_different([queens[i] - i | i in Rows]);

solve satisfy;
output ["{\"queens\": ", showJSON(queens), "}"];
