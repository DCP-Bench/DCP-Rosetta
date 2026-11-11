% sudoku: a MiniZinc model from DCP Rosetta.
%
% The goal of Sudoku is to fill a 9x9 grid with numbers so that each row, column and 3x3 section
% contain all the digits between 1 and 9. Input is a grid with some cells filled with numbers and
% some empty.
%
% Save this file as model.mzn. Download `sudoku.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py sudoku.json
%   minizinc model.mzn sudoku_1.json

include "globals.mzn";

array[int, int] of int: input_grid;             % input_grid[r,c]: the given digit in cell (r,c), 0 if empty
set of int: Rows = index_set_1of2(input_grid);  % the rows of the grid
set of int: Cols = index_set_2of2(input_grid);  % the columns of the grid
set of int: Digits = 1..9;                      % the digits to place
int: box = 3;                                   % side of a 3 x 3 section
set of int: Sections = 0..card(Rows) div box - 1;  % index of a section along one side

array[Rows, Cols] of var Digits: grid;          % grid[r,c]: the digit in cell (r,c)

% the given digits stay
constraint forall(r in Rows, c in Cols where input_grid[r,c] != 0)(grid[r,c] = input_grid[r,c]);

% each row holds each digit once
constraint forall(r in Rows)(all_different([grid[r,c] | c in Cols]));

% each column holds each digit once
constraint forall(c in Cols)(all_different([grid[r,c] | r in Rows]));

% each 3 x 3 section holds each digit once
constraint forall(i, j in Sections)(
    all_different([grid[r,c] | r in i * box + 1..(i + 1) * box, c in j * box + 1..(j + 1) * box]));

solve satisfy;
output ["{\"grid\": ", showJSON(grid), "}"];
