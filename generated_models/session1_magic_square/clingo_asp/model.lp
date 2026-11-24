% session1_magic_square: a clingo model from DCP Rosetta.
%
% A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 and the sum of the integers in each row, column and diagonal is equal. Find a magic square for a given size n, knowing that the sum of integers of each row, column and diagonal has to be equal to n(n^2+ 1)/2 (integer).
%
% Save this file as model.lp. Download `session1_magic_square.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session1_magic_square.json
%   python -m clingo model.lp session1_magic_square_1.lp

% Input: n(N): the size N of the square; cells are indexed 0..N-1 by row and column.
cell(0..N-1) :- n(N).
value(1..N*N) :- n(N).

% the sum that every row, column and diagonal has to reach
magic_sum(N*(N*N+1)/2) :- n(N).

% each cell holds exactly one number
1 { square(I,J,V) : value(V) } 1 :- cell(I), cell(J).

% each number from 1 to n^2 is used in exactly one cell
1 { square(I,J,V) : cell(I), cell(J) } 1 :- value(V).

% each row adds up to the magic sum
:- magic_sum(S), cell(I), S != #sum { V,J : square(I,J,V) }.

% each column adds up to the magic sum
:- magic_sum(S), cell(J), S != #sum { V,I : square(I,J,V) }.

% the diagonal from the top left to the bottom right adds up to the magic sum
:- magic_sum(S), S != #sum { V,I : square(I,I,V) }.

% the diagonal from the top right to the bottom left adds up to the magic sum
:- magic_sum(S), n(N), S != #sum { V,I,J : square(I,J,V), I + J == N - 1 }.

#show square/3.
