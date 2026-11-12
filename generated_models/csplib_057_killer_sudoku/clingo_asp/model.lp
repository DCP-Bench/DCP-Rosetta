% csplib_057_killer_sudoku: a clingo model from DCP Rosetta.
%
% Killer sudoku combines elements of sudoku and kakuro. The objective is to fill the grid with numbers from 1 to 9
% in a way that the following conditions are met:
%
% - Each row, column, and nonet (3x3 block) contains each number exactly once.
% - The sum of all numbers in a cage must match the small number printed in its corner.
% - No number appears more than once in a cage. (This implies that no cage can include more than 9 cells.)
%
% Save this file as model.lp. Download `csplib_057_killer_sudoku.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_057_killer_sudoku.json
%   python -m clingo model.lp csplib_057_killer_sudoku_1.lp

% Input: n(N): the size N of the grid (N = 9). problem(K, 0, S): the cage K has the sum S. problem(K, 1, J, D, V):
% the J-th cell of cage K has coordinate D in the grid (D = 0 for the row, D = 1 for the column), with V
% counted from 1 (the cage indices K and J are 0-based, as in the data).

row(0..N-1) :- n(N).
column(0..N-1) :- n(N).
digit(1..N) :- n(N).
cage(K) :- problem(K,0,_).

% the cells of each cage, with 0-based rows and columns
in_cage(K,R,C) :- problem(K,1,J,0,R0), problem(K,1,J,1,C0), R = R0-1, C = C0-1.

% each cell holds exactly one digit
1 { x(R,C,V) : digit(V) } 1 :- row(R), column(C).

% each row contains each digit exactly once
:- x(R,C1,V), x(R,C2,V), C1 < C2.

% each column contains each digit exactly once
:- x(R1,C,V), x(R2,C,V), R1 < R2.

% each nonet (3x3 block) contains each digit exactly once
:- x(R1,C1,V), x(R2,C2,V), R1*9+C1 < R2*9+C2, R1/3 == R2/3, C1/3 == C2/3.

% no number appears more than once in a cage
:- cage(K), digit(V), #count { R,C : in_cage(K,R,C), x(R,C,V) } > 1.

% the sum of the numbers in each cage matches the sum printed in its corner
:- cage(K), problem(K,0,S), #sum { V,R,C : in_cage(K,R,C), x(R,C,V) } != S.

#show x/3.
