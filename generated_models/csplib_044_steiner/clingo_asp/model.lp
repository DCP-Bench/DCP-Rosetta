% csplib_044_steiner: a clingo model from DCP Rosetta.
%
% The ternary Steiner problem of order n consists of finding a set of n * (n-1) / 6 triples of distinct
% integer elements in {1, ..., n} such that any two triples have at most one common element. It is a
% hypergraph problem coming from combinatorial mathematics where n modulo 6 has to be equal to 1 or 3.
%
% Save this file as model.lp. Download `csplib_044_steiner.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_044_steiner.json
%   python -m clingo model.lp csplib_044_steiner_1.lp

% Input: n(N): the order N of the system. The elements are 0..N-1 (the 0-based positions of the
% matrix columns), and the triples are numbered 0..T-1 with T = N * (N-1) / 6.

triple_count(N*(N-1)/6) :- n(N).
triple(0..T-1) :- triple_count(T).
element(0..N-1) :- n(N).

% each triple consists of three distinct elements
3 { in(T,E) : element(E) } 3 :- triple(T).

% any two triples have at most one common element
:- triple(T1), triple(T2), T1 < T2, #count { E : in(T1,E), in(T2,E) } > 1.

% the matrix: sets(T,E) is true when element E is part of triple T
sets(T,E,true) :- in(T,E).
sets(T,E,false) :- triple(T), element(E), not in(T,E).

#show sets/3.
