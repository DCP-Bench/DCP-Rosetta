% csplib_024_langford: a clingo model from DCP Rosetta.
%
% Consider two sets of the numbers from 1 to k. The problem is to arrange the 2k numbers in the two sets into a single sequence in which the two 1's appear one number apart, the two 2's appear two numbers apart, ..., and the two k's appear k numbers apart.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
% Save this file as model.lp. Download `csplib_024_langford.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_024_langford.json
%   python -m clingo model.lp csplib_024_langford_1.lp

% Input: k(K): the number K of pairs, so the numbers are 1..K and the sequence has 2K positions (0-based).

number(1..K) :- k(K).
pos(0..2*K-1) :- k(K).

% first(V,P): the first copy of number V is at position P, and the second copy is V+1 positions later,
% so that exactly V numbers lie between the two copies
1 { first(V,P) : pos(P), P + V + 1 < 2*K } 1 :- number(V), k(K).

% sol(P,V): position P holds the number V; each copy of V is at its two positions
sol(P,V)     :- first(V,P).
sol(P+V+1,V) :- first(V,P).

% every position holds exactly one number
:- pos(P), #count { V : sol(P,V) } != 1.

#show sol/2.
