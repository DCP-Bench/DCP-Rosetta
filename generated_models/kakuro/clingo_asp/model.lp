% kakuro: a clingo model from DCP Rosetta.
%
% The object of the puzzle is to insert a digit from 1 to 9 inclusive into each white cell such that the sum
% of the numbers in each entry matches the clue associated with it and that no digit is duplicated in any
% entry.
%
% Save this file as model.lp. Download `kakuro.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py kakuro.json
%   python -m clingo model.lp kakuro_1.lp
%
% Input: n(N) holds the size N of the grid. problem(K, 0, S) holds the clue S of entry K (0-based), and
% problem(K, J, 0, R) and problem(K, J, 1, C) hold the row R and column C of its J-th cell (J counts from 1).
% blanks(I, 0, R) and blanks(I, 1, C) hold the row R and column C of the I-th black cell. The rows and columns
% of the data count from 1; the grid here counts from 0.

index(0..N-1) :- n(N).

% x(R, C, V): the cell in row R and column C holds the digit V, where 0 is a black cell
1 { x(R,C,V) : V = 0..9 } 1 :- index(R), index(C).

% black(R, C): the cell in row R and column C is black
black(R-1,C-1) :- blanks(I,0,R), blanks(I,1,C).

% a black cell holds 0
:- black(R,C), x(R,C,V), V != 0.

% every white cell holds a digit from 1 to 9
:- index(R), index(C), not black(R,C), x(R,C,0).

% entry(K, R, C): the cell in row R and column C belongs to entry K
entry(K,R-1,C-1) :- problem(K,J,0,R), problem(K,J,1,C).

% clue(K, S): the clue of entry K is S
clue(K,S) :- problem(K,0,S).

% the digits of each entry add up to its clue
:- clue(K,S), S != #sum { V,R,C : entry(K,R,C), x(R,C,V) }.

% no digit is repeated within an entry
:- entry(K,R1,C1), entry(K,R2,C2), (R1,C1) < (R2,C2), x(R1,C1,V), x(R2,C2,V).

#show x/3.
