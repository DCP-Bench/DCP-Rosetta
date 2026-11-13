% session2_maximal_independent_sets: an ECLiPSe model from DCP Rosetta.
%
% In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal
% independent set is an independent set that is not a subset of any other independent set. A graph may have many
% maximal independent sets of widely varying sizes: find a maximal independent set for the data provided. The data
% provides an array containing for each node of the graph the set of adjacent nodes.
%
% Save this file as model.ecl. Download `session2_maximal_independent_sets.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session2_maximal_independent_sets.json
%   eclipse -b model.ecl -e "run('session2_maximal_independent_sets_1.dat'), halt"
%
% The data fields: n is the number of nodes, numbered from 1; adjacency_list holds, for node I (the I-th list), the
% numbers of the nodes adjacent to it.

:- lib(ic).
:- lib(listut).

% Output nodes: 1 when the node is in the maximal independent set, 0 otherwise.
model(Instance, Xs, [nodes-Xs]) :-
    memberchk(n-N, Instance),
    memberchk(adjacency_list-Adjacency, Instance),
    length(Xs, N),
    Xs :: 0..1,

    ( for(I, 1, N), param(Adjacency, Xs) do
        nth1(I, Adjacency, Adj),
        nth1(I, Xs, XI),
        ( foreach(J, Adj), param(Xs), foreach(XJ, Neighbours) do
            nth1(J, Xs, XJ)
        ),

        % a node in the set has no neighbour in the set
        ( foreach(XJ, Neighbours), param(XI) do
            XI + XJ #=< 1
        ),

        % a node outside the set has a neighbour in the set, so the set cannot be extended
        XI + sum(Neighbours) #>= 1
    ).

:- lib(branch_and_bound).

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
