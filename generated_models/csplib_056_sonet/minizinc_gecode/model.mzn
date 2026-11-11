% csplib_056_sonet: a MiniZinc model from DCP Rosetta.
%
% In the SONET problem, we are given a set of nodes and the traffic demand for each pair of nodes. The nodes
% are connected by a set of rings. A node is installed on a ring using an add-drop multiplexer (ADM). For two
% nodes to communicate, they must be on at least one common ring. Each ring has a capacity, limiting the
% number of nodes it can host. The objective is to satisfy all communication demands while minimizing the
% total number of ADMs used.
%
% Save this file as model.mzn. Download `csplib_056_sonet.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_056_sonet.json
%   minizinc model.mzn csplib_056_sonet_1.json

int: n;                                          % the number of nodes
int: r;                                          % the number of rings
array[int, int] of int: demand;                  % demand[i,j]: the traffic between nodes i and j
array[int] of int: capacity_nodes;               % capacity_nodes[k]: the number of nodes ring k can host

set of int: Nodes = 1..n;                        % the nodes
set of int: Rings = 1..r;                        % the rings

% ring_config[k,i]: node i is on ring k
array[Rings, Nodes] of var bool: ring_config;

% the total number of ADMs, one for each node on a ring
var int: total_adms = sum(k in Rings, i in Nodes)(bool2int(ring_config[k, i]));
var int: objective = total_adms;

% two nodes with traffic between them are on at least one common ring
constraint forall(i, j in Nodes where i < j /\ (demand[i, j] > 0 \/ demand[j, i] > 0))(
    exists(k in Rings)(ring_config[k, i] /\ ring_config[k, j]));

% each ring hosts no more nodes than its capacity
constraint forall(k in Rings)(sum(i in Nodes)(bool2int(ring_config[k, i])) <= capacity_nodes[k]);

solve minimize objective;
output ["{\"ring_config\": ", showJSON(ring_config), ", \"total_adms\": ", show(total_adms), "}"];
