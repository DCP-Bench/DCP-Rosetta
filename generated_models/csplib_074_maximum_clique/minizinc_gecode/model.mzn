% csplib_074_maximum_clique: a MiniZinc model from DCP Rosetta.
%
% Given a simple undirected graph G = (V, E), a clique is a subset of vertices V where every two distinct
% vertices in the subset are adjacent (connected by an edge). The maximum clique problem is to find a clique
% of the largest possible size in the given graph.
%
% Save this file as model.mzn. Download `csplib_074_maximum_clique.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_074_maximum_clique.json
%   minizinc model.mzn csplib_074_maximum_clique_1.json

int: n;                                          % the number of vertices
array[int, int] of int: adj;                     % adj[i,j] = 1 if vertices i and j are adjacent, 0 otherwise

set of int: Vertices = 1..n;                     % the vertices

% c[i]: vertex i is in the clique
array[Vertices] of var bool: c;

% the number of vertices in the clique, to be maximised
var int: objective = sum(i in Vertices)(bool2int(c[i]));

% any two distinct vertices of the clique are adjacent, so no two non-adjacent vertices are both in it
constraint forall(i, j in Vertices where i < j /\ adj[i, j] = 0)(not (c[i] /\ c[j]));

solve maximize objective;
output ["{\"c\": ", showJSON(c), "}"];
