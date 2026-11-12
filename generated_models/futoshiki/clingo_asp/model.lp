% futoshiki: a clingo model from DCP Rosetta.
%
% The futoshiki puzzle is played on a square grid, such as 5 x 5. The objective is to place the numbers 1 to 5
% (or whatever the dimensions are) such that each row, and each column contains each of the digits 1 to 5.
% Some digits may be given at the start. In addition, inequality constraints are also initially specified
% between some of the squares, such that one must be higher or lower than its neighbour. These constraints
% must be honoured as the grid is filled out.
%
% Save this file as model.lp. Download `futoshiki.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py futoshiki.json
%   python -m clingo model.lp futoshiki_1.lp
%
% Input: values(R, C, V) holds the given digit V at row R and column C, counted from 0 (V = 0 for an empty
% cell); lt(K, F, V) holds the value V of the field F of the K-th inequality sign, where F = 0 and 1 are the
% row and column (counted from 1) of the cell that must be smaller, and F = 2 and 3 the row and column of the
% cell that must be larger.

% the grid is n x n, with rows and columns 0 to n-1 and digits 1 to n
size(N) :- N = #count { R : values(R, 0, _) }.
index(0..N-1) :- size(N).
digit(1..N) :- size(N).

% each cell holds exactly one digit: grid(R, C, V) holds when cell (R, C) holds the digit V
1 { grid(R, C, V) : digit(V) } 1 :- index(R), index(C).

% the given digits stay in their cells
:- values(R, C, V), V > 0, not grid(R, C, V).

% each row holds each digit once
:- grid(R, C1, V), grid(R, C2, V), C1 < C2.

% each column holds each digit once
:- grid(R1, C, V), grid(R2, C, V), R1 < R2.

% each inequality sign: the smaller cell holds a smaller digit than the larger cell
:- lt(K, 0, R1), lt(K, 1, C1), lt(K, 2, R2), lt(K, 3, C2),
   grid(R1 - 1, C1 - 1, A), grid(R2 - 1, C2 - 1, B), A >= B.

#show grid/3.
