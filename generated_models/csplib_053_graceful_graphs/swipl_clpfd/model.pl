% csplib_053_graceful_graphs: a SWI-Prolog model from DCP Rosetta.
%
% A labelling of the nodes of a graph with m edges is graceful when each node gets a different label from 0 to m,
% and when each edge xy is labelled with the absolute difference |f(x) - f(y)| of its end labels, all the edge
% labels are different. Find a graceful labelling of the graph, and give the node labels and the edge labels, the
% latter in the order of the edges.
%
% Save this file as model.pl. Download `csplib_053_graceful_graphs.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_053_graceful_graphs.json')" -t halt model.pl
%
% Data fields: graph (the edges, each a pair of node numbers indexed from 0), m (the number of edges), n (the number
% of nodes).
:- use_module(library(clpfd)).

model(Instance, Vars, [nodes-Nodes, edges-Labels]) :-
    Edges = Instance.graph,
    M = Instance.m, N = Instance.n,
    % the node labels: N different labels from 0 to M
    length(Nodes, N), Nodes ins 0..M,
    all_distinct(Nodes),
    % the edge labels: the absolute differences of the end labels, all different and from 1 to M
    maplist(edge_label(Nodes), Edges, Labels),
    Labels ins 1..M,
    all_distinct(Labels),
    append(Nodes, Labels, Vars).

edge_label(Nodes, [X, Y], Label) :-
    nth0(X, Nodes, FX),
    nth0(Y, Nodes, FY),
    Label #= abs(FX - FY).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
