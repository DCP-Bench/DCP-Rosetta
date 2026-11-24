% csplib_053_graceful_graphs: a clingo model from DCP Rosetta.
%
% A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label
% from {0, 1, ..., q} and when each edge xy is labelled with |f(x) - f(y)|, the edge labels are all different.
%
% Save this file as model.lp. Download `csplib_053_graceful_graphs.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_053_graceful_graphs.json
%   python -m clingo model.lp csplib_053_graceful_graphs_1.lp

% Input: n(N): the number N of nodes, numbered 0..N-1; m(Q): the number Q of edges, numbered 0..Q-1;
% graph(E, K, V): node V is the K-th end (K is 0 or 1) of edge E (indices are 0-based, as in the data).

node(0..N-1) :- n(N).
edge(0..Q-1) :- m(Q).
label(0..Q) :- m(Q).

% each node gets exactly one label from {0, ..., q}
1 { nodes(V,L) : label(L) } 1 :- node(V).

% the labels of the nodes are unique
:- label(L), #count { V : nodes(V,L) } > 1.

% the label of each edge is the difference of the labels of its two end nodes
edges(E,D) :- edge(E), graph(E,0,U), graph(E,1,W), nodes(U,A), nodes(W,B), D = |A-B|.

% the labels of the edges are all different
:- edges(E1,D), edges(E2,D), E1 < E2.

#show nodes/2.
#show edges/2.
