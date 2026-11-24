% csplib_012_nonogram: a clingo model from DCP Rosetta.
%
% Nonograms are puzzles in which the squares of a grid are shaded so that the blocks of consecutive shaded squares
% satisfy the constraints (clues) given for each row and each column. A clue such as 3,1,2 means a block of 3, then a
% gap of unspecified size, a block of 1, another gap, and then a block of 2. Find a shading of the grid that
% satisfies the clues of all rows and all columns.
%
% Save this file as model.lp. Download `csplib_012_nonogram.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_012_nonogram.json
%   python -m clingo model.lp csplib_012_nonogram_1.lp
%
% Input: rows(R), cols(C): the number of rows R and of columns C; row_rules(R,K,L): the block length L at position K
% of the clue of row R; col_rules(C,K,L): the same for column C. Clues are padded with zeros, and a zero means no block
% (indices are 0-based, as in the data).

row(0..R-1) :- rows(R).
col(0..C-1) :- cols(C).

% the blocks of a clue, numbered from 0 in order, skipping the zeros of the padding
rblock(R,N,L) :- row_rules(R,K,L), L > 0, N = #count { K2 : row_rules(R,K2,L2), L2 > 0, K2 < K }.
cblock(C,N,L) :- col_rules(C,K,L), L > 0, N = #count { K2 : col_rules(C,K2,L2), L2 > 0, K2 < K }.

% h_start(R,N,S): block N of row R starts at column S; it must fit in the row
1 { h_start(R,N,S) : col(S), S + L <= C } 1 :- rblock(R,N,L), cols(C).
% v_start(C,N,S): block N of column C starts at row S; it must fit in the column
1 { v_start(C,N,S) : row(S), S + L <= R } 1 :- cblock(C,N,L), rows(R).

% the blocks of a row are in order, with at least one unshaded square between two blocks
:- h_start(R,N,S), h_start(R,N+1,S2), rblock(R,N,L), S2 < S + L + 1.
:- v_start(C,N,S), v_start(C,N+1,S2), cblock(C,N,L), S2 < S + L + 1.

% shaded squares are those covered by the blocks of the rows
rshaded(R,C) :- h_start(R,N,S), rblock(R,N,L), col(C), S <= C, C < S + L.
% shaded squares are those covered by the blocks of the columns
cshaded(R,C) :- v_start(C,N,S), cblock(C,N,L), row(R), S <= R, R < S + L.

% the rows and the columns agree on every square
:- rshaded(R,C), not cshaded(R,C).
:- cshaded(R,C), not rshaded(R,C).

% board(R,C,V): square (R,C) is shaded (1) or not (0)
board(R,C,1) :- rshaded(R,C).
board(R,C,0) :- row(R), col(C), not rshaded(R,C).

#show board/3.
