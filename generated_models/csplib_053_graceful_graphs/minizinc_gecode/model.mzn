% csplib_053_graceful_graphs: a MiniZinc model from DCP Rosetta.
%
% A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label
% from {0, 1, ..., q} and, when each edge xy is labelled with |f(x) - f(y)|, the edge labels are all
% different. Find a graceful labelling of the given graph.
%
% Save this file as model.mzn. Download `csplib_053_graceful_graphs.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_053_graceful_graphs.json
%   minizinc model.mzn csplib_053_graceful_graphs_1.json

include "globals.mzn";

int: m;                                          % the number of edges
int: n;                                          % the number of nodes
array[int, int] of int: graph;                   % graph[e,1], graph[e,2]: the two nodes of edge e, numbered from 0

set of int: Nodes = 1..n;                        % the nodes, node v of the data is position v+1 here
set of int: Edges = 1..m;                        % the edges

array[Nodes] of var 0..m: nodes;                 % nodes[v]: the label of node v
array[Edges] of var 1..m: edges;                 % edges[e]: the label of edge e

% each node has a unique label
constraint all_different(nodes);

% each edge is labelled with the difference of the labels of its two nodes
constraint forall(e in Edges)(edges[e] = abs(nodes[graph[e, 1] + 1] - nodes[graph[e, 2] + 1]));

% all edge labels are different
constraint all_different(edges);

solve satisfy;
output ["{\"nodes\": ", showJSON(nodes), ", \"edges\": ", showJSON(edges), "}"];
