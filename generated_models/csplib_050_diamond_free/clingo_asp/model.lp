% csplib_050_diamond_free: a clingo model from DCP Rosetta.
%
% Given a simple undirected graph G = (V, E), where V is the set of vertices and E the set of undirected edges,
% the edge {u, v} is in E if and only if vertex u is adjacent to vertex v in G. The graph is simple in that there
% are no loop edges, i.e., no edges of the form {v, v}. A diamond is a set of four vertices in V such that there
% are at least five edges between those vertices. A graph is diamond-free if it has no diamond as an induced
% subgraph, i.e., for every set of four vertices the number of edges between those vertices is at most four.
%
% The degree of each vertex must be greater than zero (isolated vertices are disallowed) and divisible by 3, and
% the sum of the degrees must be divisible by 12 (i.e., the number of edges is divisible by 6).
%
% Save this file as model.lp. Download `csplib_050_diamond_free.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_050_diamond_free.json
%   python -m clingo model.lp csplib_050_diamond_free_1.lp

% Input: n(N): the number N of vertices, numbered 0..N-1 (indices are 0-based).

vertex(0..N-1) :- n(N).

% each pair of distinct vertices is joined by an edge or not; edge(U,V) is stored with U < V
{ edge(U,V) : vertex(U), vertex(V), U < V }.
adj(U,V) :- edge(U,V).
adj(V,U) :- edge(U,V).

% the degree of each vertex is the number of its neighbours
degree(U,D) :- vertex(U), D = #count { V : adj(U,V) }.

% the degree of each vertex is greater than zero and divisible by 3
:- degree(U,D), D <= 0.
:- degree(U,D), D \ 3 != 0.

% the sum of the degrees is divisible by 12
total_degree(S) :- S = #sum { D,U : degree(U,D) }.
:- total_degree(S), S \ 12 != 0.

% no four vertices span five or more edges
:- vertex(A), vertex(B), vertex(C), vertex(D), A < B, B < C, C < D,
   #count { 1,A,B : edge(A,B); 1,A,C : edge(A,C); 1,A,D : edge(A,D);
            1,B,C : edge(B,C); 1,B,D : edge(B,D); 1,C,D : edge(C,D) } > 4.

% the adjacency matrix: matrix(U,V) is true when U and V are adjacent
matrix(U,V,true) :- adj(U,V).
matrix(U,V,false) :- vertex(U), vertex(V), not adj(U,V).

#show matrix/3.
