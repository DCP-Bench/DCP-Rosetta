% session2_maximal_independent_sets: a MiniZinc model from DCP Rosetta.
%
% In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal
% independent set is an independent set that is not a subset of any other independent set. A graph may have many
% maximal independent sets of widely varying sizes: find a maximal independent set of the graph. Each node of the graph
% has a set of adjacent nodes.
%
% Save this file as model.mzn. Download `session2_maximal_independent_sets.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py session2_maximal_independent_sets.json
%   minizinc model.mzn session2_maximal_independent_sets_1.json

int: n;                                                 % the number of nodes
array[int, int] of int: adjacency_list;                 % adjacency_list[i,k]: the k-th node adjacent to node i (rows padded with 0 when nodes have different degrees)
array[int] of int: adjacency_list_len;                  % adjacency_list_len[i]: the number of nodes adjacent to node i (added by the conversion)

set of int: Nodes = 1..n;                               % one index per node

array[Nodes] of var bool: nodes;                        % nodes[i]: node i is in the independent set

% no two nodes of the set are adjacent
constraint forall(i in Nodes, k in 1..adjacency_list_len[i])(not (nodes[i] /\ nodes[adjacency_list[i, k]]));

% the set cannot be extended: every node outside it is adjacent to a node in it
constraint forall(i in Nodes)(nodes[i] \/ exists(k in 1..adjacency_list_len[i])(nodes[adjacency_list[i, k]]));

solve satisfy;
output ["{\"nodes\": ", showJSON(nodes), "}"];
