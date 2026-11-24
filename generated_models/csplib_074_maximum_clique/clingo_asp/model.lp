% csplib_074_maximum_clique: a clingo model from DCP Rosetta.
%
% Given a simple undirected graph G = (V, E), a clique is a subset of vertices V where every two distinct
% vertices in the subset are adjacent (connected by an edge). The maximum clique problem is to find a clique
% of the largest possible size in a given graph.
%
% Save this file as model.lp. Download `csplib_074_maximum_clique.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_074_maximum_clique.json
%   python -m clingo model.lp csplib_074_maximum_clique_1.lp

% Input: n(N): the number N of vertices, numbered 0..N-1; adj(U, V, A): A is 1 when vertices U and V are
% joined by an edge and 0 otherwise (indices are 0-based, as in the data).

vertex(0..N-1) :- n(N).

% two vertices are joined when the adjacency matrix says so, in either direction
joined(U,V) :- adj(U,V,1).
joined(U,V) :- adj(V,U,1).

% each vertex is either in the clique or not
{ in(V) : vertex(V) }.

% every two distinct vertices in the clique are adjacent
:- in(U), in(V), U < V, not joined(U,V).

% the clique is as large as possible
#maximize { 1,V : in(V) }.

% c(V, true) when vertex V is in the clique, c(V, false) otherwise
c(V,true) :- in(V).
c(V,false) :- vertex(V), not in(V).

#show c/2.
