% csplib_056_sonet: a clingo model from DCP Rosetta.
%
% In the SONET problem, we are given a set of nodes and the traffic demand for each pair of nodes. The nodes
% are connected by a set of rings. A node is installed on a ring using an add-drop multiplexer (ADM). For two
% nodes to communicate, they must be on at least one common ring. Each ring has a capacity, limiting the number
% of nodes it can host. The objective is to satisfy all communication demands while minimizing the total number
% of ADMs used.
%
% Save this file as model.lp. Download `csplib_056_sonet.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_056_sonet.json
%   python -m clingo model.lp csplib_056_sonet_1.lp

% Input: n(N): the number N of nodes; r(R): the number R of rings; capacity_nodes(K, C): the capacity C of ring K;
% demand(I, J, D): the traffic demand D from node I to node J (indices are 0-based, as in the data).

node(0..N-1) :- n(N).
ring(0..R-1) :- r(R).

% each node is installed on some rings: on(K,I) is true when node I is on ring K
{ on(K,I) : ring(K) } :- node(I).

% each ring hosts no more nodes than its capacity
:- capacity_nodes(K,C), #count { I : on(K,I) } > C.

% two nodes share a ring when they are both on it
shares(I,J) :- on(K,I), on(K,J), I != J.

% every pair of nodes with a positive demand between them shares at least one ring
:- demand(I,J,D), D > 0, I != J, not shares(I,J).

% the total number of ADMs is as small as possible: one ADM for each node on each ring
total_adms(T) :- T = #count { K,I : on(K,I) }.
#minimize { 1,K,I : on(K,I) }.

% ring_config(K, I, V): V is true when node I is on ring K
ring_config(K,I,true) :- on(K,I).
ring_config(K,I,false) :- ring(K), node(I), not on(K,I).

#show total_adms/1.
#show ring_config/3.
