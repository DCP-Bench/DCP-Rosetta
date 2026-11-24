% csplib_007_all_interval: a clingo model from DCP Rosetta.
%
% Find a series s_1, ..., s_n, a permutation of 0, 1, ..., n-1, such that the intervals between neighbouring
% entries, |s_2 - s_1|, |s_3 - s_2|, ..., |s_n - s_(n-1)|, are a permutation of 1, 2, ..., n-1. Such a series is
% an all-interval series of size n.
%
% Save this file as model.lp. Download `csplib_007_all_interval.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_007_all_interval.json
%   python -m clingo model.lp csplib_007_all_interval_1.lp
%
% Input: n(N) holds the number N of pitch classes (indices are 0-based, as in the data).

% the positions of the series and the pitch classes it may use
position(0..N-1) :- n(N).
pitch(0..N-1) :- n(N).

% x(I,P): the series has pitch class P at position I
1 { x(I,P) : pitch(P) } 1 :- position(I).

% each pitch class occurs exactly once in the series
1 { x(I,P) : position(I) } 1 :- pitch(P).

% diffs(I,D): the interval between the neighbouring entries at positions I and I + 1 is D
diffs(I,D) :- x(I,P), x(I+1,Q), D = |P - Q|.

% each interval from 1 to n - 1 occurs exactly once among the neighbouring pairs
interval(1..N-1) :- n(N).
:- interval(D), #count { I : diffs(I,D) } != 1.

#show x/2.
#show diffs/2.
