% hidato: a MiniZinc model from DCP Rosetta.
%
% Hidato puzzles start semi-filled with numbered tiles. Connect the numbers together to win: consecutive
% numbers must touch horizontally, vertically, or diagonally, and the numbers must be in increasing order.
% Fill in the empty cells, marked 0 in the given puzzle, with the numbers that complete the puzzle, so that
% the grid holds each number from 1 to the number of cells exactly once.
%
% Save this file as model.mzn. Download `hidato.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py hidato.json
%   minizinc model.mzn hidato_1.json

include "globals.mzn";

array[int, int] of int: puzzle;                  % the given grid, 0 marks an empty cell

set of int: Rows = index_set_1of2(puzzle);       % the grid's rows
set of int: Cols = index_set_2of2(puzzle);       % the grid's columns
int: nr = card(Rows);                            % number of rows
int: nc = card(Cols);                            % number of columns
int: cells = nr * nc;                            % number of cells, and the largest number

% x[i,j]: the number in the cell in row i, column j
array[Rows, Cols] of var 1..cells: x;

% place[k]: the position (counted row by row from 1) of the cell holding the number k
array[1..cells] of var 1..cells: place;

% every number from 1 to the number of cells is used exactly once
constraint all_different([x[i, j] | i in Rows, j in Cols]);

% the given numbers stay in their cells
constraint forall(i in Rows, j in Cols where puzzle[i, j] > 0)(x[i, j] = puzzle[i, j]);

% place is the inverse of x, reading the grid row by row
constraint inverse([x[i, j] | i in Rows, j in Cols], place);

% the row and column of the cell holding number k
array[1..cells] of var Rows: row_of = [min(Rows) + (place[k] - 1) div nc | k in 1..cells];
array[1..cells] of var Cols: col_of = [min(Cols) + (place[k] - 1) mod nc | k in 1..cells];

% consecutive numbers k and k+1 lie in touching cells, horizontally, vertically or diagonally
constraint forall(k in 1..cells - 1)(abs(row_of[k] - row_of[k + 1]) <= 1 /\ abs(col_of[k] - col_of[k + 1]) <= 1);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
