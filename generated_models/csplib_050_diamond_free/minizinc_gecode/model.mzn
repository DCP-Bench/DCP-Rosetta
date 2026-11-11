% csplib_050_diamond_free: a MiniZinc model from DCP Rosetta.
%
% Find a simple undirected graph on N vertices that is diamond-free, i.e. has no four vertices with at
% least five edges between them, such that every vertex has a degree greater than zero that is divisible
% by 3, and the sum of the degrees is divisible by 12 (so the number of edges is divisible by 6).
%
% Save this file as model.mzn. Download `csplib_050_diamond_free.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_050_diamond_free.json
%   minizinc model.mzn csplib_050_diamond_free_1.json

int: N;                                          % the number of vertices

set of int: Vertices = 1..N;                     % the vertices

% adj[u,v]: the edge {u, v} is in the graph
array[Vertices, Vertices] of var bool: adj;

% the graph has no loop edges and each edge is undirected
constraint forall(v in Vertices)(adj[v, v] = false);
constraint forall(u, v in Vertices)(adj[u, v] = adj[v, u]);

% degree[v]: the number of edges incident on vertex v
array[Vertices] of var 0..N - 1: degree;
constraint forall(v in Vertices)(degree[v] = sum(u in Vertices)(bool2int(adj[v, u])));

% the degree of each vertex is greater than zero and divisible by 3
constraint forall(v in Vertices)(degree[v] > 0 /\ degree[v] mod 3 = 0);

% the sum of the degrees is divisible by 12
constraint sum(degree) mod 12 = 0;

% the graph is diamond-free: any four vertices have at most four edges between them
constraint forall(a, b, c, d in Vertices where a < b /\ b < c /\ c < d)(
    bool2int(adj[a, b]) + bool2int(adj[a, c]) + bool2int(adj[a, d]) +
    bool2int(adj[b, c]) + bool2int(adj[b, d]) + bool2int(adj[c, d]) <= 4);

solve satisfy;
output ["{\"matrix\": ", showJSON(adj), "}"];
