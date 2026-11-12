% minesweeper: a clingo model from DCP Rosetta.
%
% Minesweeper rules are very simple. The board is divided into cells, with mines distributed among them. The number on an opened cell shows the number of mines adjacent to it. The task is to determine which 'X' fields contain mines based on the provided numerical clues.
%
% Save this file as model.lp. Download `minesweeper.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py minesweeper.json
%   python -m clingo model.lp minesweeper_1.lp
%
% Input: x(X) the marker X of an unopened cell; game_data(R, C, V) the value V of the cell in row R and column C,
% equal to the marker when the cell is unopened (indices are 0-based, as in the data).

cell(R,C) :- game_data(R,C,_).

% mine(R,C): the cell in row R and column C holds a mine
{ mine(R,C) } :- cell(R,C).

% mines(R,C,B): B is 1 when the cell holds a mine, and 0 when it does not
mines(R,C,1) :- mine(R,C).
mines(R,C,0) :- cell(R,C), not mine(R,C).

% an opened cell does not hold a mine
:- x(X), game_data(R,C,V), V != X, mine(R,C).

% the number on an opened cell is the number of mines among its neighbours
:- x(X), game_data(R,C,V), V != X,
   V != #count { A,B : mine(A,B), |A - R| <= 1, |B - C| <= 1, (A,B) != (R,C) }.

#show mines/3.
