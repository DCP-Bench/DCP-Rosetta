% heterosquare: a clingo model from DCP Rosetta.
%
% A heterosquare of order n is an n by n square whose elements are distinct integers from 1 to n^2 such
% that the sums of the rows, columns and diagonals are all different.
%
% Save this file as model.lp. Download `heterosquare.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py heterosquare.json
%   python -m clingo model.lp heterosquare_1.lp
%
% Input: n(N) holds the order N of the square (indices are 0-based, as in the data).

cell(0..N-1) :- n(N).
value(1..N*N) :- n(N).

% each cell of the square holds exactly one value
1 { x(I,J,V) : value(V) } 1 :- cell(I), cell(J).

% the elements of the square are distinct
:- x(I,J,V), x(K,L,V), (I,J) < (K,L).

% the sum of each row, column and diagonal (diag(1) is the main diagonal, diag(2) the other one)
total(row(I), S) :- cell(I), S = #sum { V,J : x(I,J,V) }.
total(col(J), S) :- cell(J), S = #sum { V,I : x(I,J,V) }.
total(diag(1), S) :- S = #sum { V,I : x(I,I,V) }.
total(diag(2), S) :- n(N), S = #sum { V,I : x(I,J,V), J == N - I - 1 }.

% the sums of the rows, columns and diagonals are all different
:- total(P,S), total(Q,S), P < Q.

#show x/3.
