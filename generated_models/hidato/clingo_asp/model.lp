% hidato: a clingo model from DCP Rosetta.
%
% Hidato puzzles start semi-filled with numbered tiles. Connect the numbers together to win. Consecutive
% numbers must touch horizontally, vertically, or diagonally, and the numbers must be in increasing order.
% Fill in the empty cells, marked 0 in the given puzzle, with the numbers that complete the puzzle, so that
% the grid holds each number from 1 to the number of cells exactly once.
%
% Save this file as model.lp. Download `hidato.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py hidato.json
%   python -m clingo model.lp hidato_1.lp
%
% Input: puzzle(R, C, V) holds the value V of the cell in row R and column C (indices are 0-based, as in
% the data), with V = 0 for an empty cell.

cell(R,C) :- puzzle(R,C,_).
total(N) :- N = #count { R,C : cell(R,C) }.

% each cell holds exactly one number from 1 to the number of cells
1 { x(R,C,V) : V = 1..N } 1 :- cell(R,C), total(N).

% each number from 1 to the number of cells is used exactly once
1 { x(R,C,V) : cell(R,C) } 1 :- total(N), V = 1..N.

% the numbers already filled in stay where they are
:- puzzle(R,C,V), V > 0, not x(R,C,V).

% touches(R, C, R2, C2): two different cells touch horizontally, vertically or diagonally
touches(R,C,R2,C2) :- cell(R,C), cell(R2,C2), |R - R2| <= 1, |C - C2| <= 1, |R - R2| + |C - C2| > 0.

% each number except the last one is in a cell that touches the cell of the next number
:- x(R,C,V), total(N), V < N, #count { R2,C2 : touches(R,C,R2,C2), x(R2,C2,V + 1) } == 0.

#show x/3.
