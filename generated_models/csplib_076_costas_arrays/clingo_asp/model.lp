% csplib_076_costas_arrays: a clingo model from DCP Rosetta.
%
% A Costas array is a pattern of n marks on an n x n grid, one mark per row and one per column, in which
% the n(n-1)/2 vectors between the marks are all different.
%
% Save this file as model.lp. Download `csplib_076_costas_arrays.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_076_costas_arrays.json
%   python -m clingo model.lp csplib_076_costas_arrays_1.lp

% Input: n(N) holds the size N of the array (the number of marks and of rows and columns).

% the positions are 0..N-1 and the values are 1..N
pos(0..N-1) :- n(N).
value(1..N) :- n(N).

% each position holds exactly one value
1 { costas(I,V) : value(V) } 1 :- pos(I).

% each value is held by exactly one position, so the marks are one per row and one per column
1 { costas(I,V) : pos(I) } 1 :- value(V).

% the lags of the difference triangle are 1..N-1
lag(1..N-1) :- n(N).

% line L of the difference triangle holds the differences costas(I) - costas(I+L) for I = 0..N-L-1
diff(L,I,V-W) :- n(N), lag(L), pos(I), I+L < N, costas(I,V), costas(I+L,W).

% no value occurs twice in the same line of the difference triangle
:- diff(L,I,D), diff(L,J,D), I < J.

#show costas/2.
