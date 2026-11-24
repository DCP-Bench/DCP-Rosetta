% sudoku: a clingo model from DCP Rosetta.
%
% The goal of Sudoku is to fill a 9x9 grid with numbers so that each row, column and 3x3 section contain all the digits
% between 1 and 9. The grid is given with some cells filled with numbers and some empty.
%
% Save this file as model.lp. Download `sudoku.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py sudoku.json
%   python -m clingo model.lp sudoku_1.lp
%
% Input: input_grid(R, C, V) holds the digit V of the given grid in row R and column C (0-based, as in the data);
% V is 0 for an empty cell.

cell(0..8).
digit(1..9).
block(0..2).

% each cell holds exactly one digit
1 { grid(R, C, V) : digit(V) } 1 :- cell(R), cell(C).

% the digits given in the grid stay where they are
:- input_grid(R, C, V), V > 0, not grid(R, C, V).

% each row contains each digit exactly once
:- cell(R), digit(V), #count { C : grid(R, C, V) } != 1.

% each column contains each digit exactly once
:- cell(C), digit(V), #count { R : grid(R, C, V) } != 1.

% each 3x3 section contains each digit exactly once
:- block(BR), block(BC), digit(V), #count { R, C : grid(R, C, V), R / 3 == BR, C / 3 == BC } != 1.

#show grid/3.
