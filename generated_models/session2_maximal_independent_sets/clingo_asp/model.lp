% session2_maximal_independent_sets: a clingo model from DCP Rosetta.
%
% In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal independent set is an independent set that is not a subset of any other independent set. A graph may have many maximal independent sets of widely varying sizes: find a maximal independent set for the data provided. The data provides an array containing for each node of the graph the set of adjacent nodes.
%
% Save this file as model.lp. Download `session2_maximal_independent_sets.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session2_maximal_independent_sets.json
%   python -m clingo model.lp session2_maximal_independent_sets_1.lp

% Input: n(N): the number of nodes N, numbered 1..N in the data; adjacency_list(I,K,J): the K-th
% neighbour of the node at index I is node J (1-based, as in the data; indices are 0-based).

% the nodes are indexed 0..N-1
node(0..N-1) :- n(N).

% the neighbour J (1-based) of the node at index I has index J-1
neighbour(I,J-1) :- adjacency_list(I,_,J).

% adjacency is symmetric
adjacent(I,J) :- neighbour(I,J).
adjacent(J,I) :- neighbour(I,J).

% each node is either in the set (true) or not (false)
1 { nodes(I,true); nodes(I,false) } 1 :- node(I).

% no two nodes of the set are adjacent
:- adjacent(I,J), nodes(I,true), nodes(J,true).

% the set is maximal: every node outside it has a neighbour inside it
covered(I) :- adjacent(I,J), nodes(J,true).
:- nodes(I,false), not covered(I).

#show nodes/2.
