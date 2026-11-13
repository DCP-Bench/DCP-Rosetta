% csplib_053_graceful_graphs: an ECLiPSe model from DCP Rosetta.
%
% A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label from {0, 1, ..., q}
% and, when each edge xy is labelled with |f(x) - f(y)|, the edge labels are all different. Find a graceful labelling of
% the graph.
%
% Save this file as model.ecl. Download `csplib_053_graceful_graphs.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_053_graceful_graphs.json
%   eclipse -b model.ecl -e "run('csplib_053_graceful_graphs_1.dat'), halt"
%
% The instance fields: n (the number of nodes), m (the number of edges, q), graph (the edges as pairs of node numbers,
% counting from 0).

:- lib(ic).
:- lib(branch_and_bound).

% Outputs the node labels and the edge labels, the latter in the order of the edges in graph.
model(Instance, Vars, [nodes-Nodes, edges-Labels]) :-
    memberchk(n-N, Instance),
    memberchk(m-Q, Instance),
    memberchk(graph-Graph, Instance),
    length(Nodes, N),
    Nodes :: 0..Q,

    % each node has a unique label
    alldifferent(Nodes),

    % the label of each edge is the difference of the labels of its two nodes (element/3 is 1-based)
    length(Labels, Q),
    Labels :: 1..Q,
    ( foreach([X, Y], Graph), foreach(Label, Labels), param(Nodes) do
        X1 is X + 1,
        Y1 is Y + 1,
        element(X1, Nodes, FX),
        element(Y1, Nodes, FY),
        Label #= abs(FX - FY)
    ),

    % the edge labels are all different
    alldifferent(Labels),
    append(Nodes, Labels, Vars).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
