% csplib_054_n_queens: a clingo model from DCP Rosetta.
%
% Can n queens (of the same color) be placed on an n x n chessboard so that none of the queens can attack
% each other? A queen attacks other squares on the same row, column, or either diagonal as itself. So the
% n-queens problem is to find a set of n locations on a chessboard, no two of which are on the same row,
% column or diagonal.
%
% Save this file as model.lp. Download `csplib_054_n_queens.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_054_n_queens.json
%   python -m clingo model.lp csplib_054_n_queens_1.lp

% Input: n(N): the size N of the board, which has N rows and N columns and holds N queens.

row(0..N-1) :- n(N).
column(1..N) :- n(N).

% each row holds exactly one queen, in some column
1 { queens(R,C) : column(C) } 1 :- row(R).

% no two queens share a column
:- column(C), #count { R : queens(R,C) } > 1.

% no two queens share a diagonal: the rows differ by the same amount as the columns
:- queens(R1,C1), queens(R2,C2), R1 < R2, R2 - R1 == |C2 - C1|.

#show queens/2.
