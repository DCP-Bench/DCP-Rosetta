% autoref: a clingo model from DCP Rosetta.
%
% Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S=(s0, s1, ..., sn, sn+1) of integers between 0 and n such that (1) there are si occurrences of i in S for each integer i ranging from 0 to n, and (2) sn+1=m.
%
% Save this file as model.lp. Download `autoref.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py autoref.json
%   python -m clingo model.lp autoref_1.lp

% Input: n(N) holds the integer n and m(M) the integer m (the instance values).

% the series has the positions 0 to n+1, and each entry is a value between 0 and n
pos(0..N+1) :- n(N).
value(0..N) :- n(N).

% each position of the series holds exactly one value
1 { s(I, V) : value(V) } 1 :- pos(I).

% for each i from 0 to n, the number of positions holding i is the entry s(i)
:- value(I), s(I, V), #count { J : s(J, I) } != V.

% the last entry sn+1 equals m
:- n(N), m(M), not s(N+1, M).

#show s/2.
