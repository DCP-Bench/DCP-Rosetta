% session2_maximal_independent_sets: a SWI-Prolog model from DCP Rosetta.
%
% In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal
% independent set is an independent set that is not a subset of any other independent set. Find a maximal independent
% set for the data provided. The data provides an array containing, for each node of the graph, the set of adjacent
% nodes.
%
% Save this file as model.pl. Download `session2_maximal_independent_sets.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session2_maximal_independent_sets.json')" -t halt model.pl
%
% Data fields: n (the number of nodes, numbered 1 to n), adjacency_list (for each node in turn, the nodes adjacent to
% it, numbered from 1; the list is indexed from 0, so the row at index 0 is node 1).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

model(Instance, Nodes, [nodes-Nodes]) :-
    N = Instance.n,
    Adjacency = Instance.adjacency_list,
    length(Nodes, N),                      % Nodes[I-1] is 1 when node I is in the set, 0 otherwise
    Nodes ins 0..1,
    numlist(1, N, Ids),
    maplist(check_node(Nodes, Adjacency), Ids).

% check_node(+Nodes, +Adjacency, +I): the two requirements for node I.
check_node(Nodes, Adjacency, I) :-
    nth1(I, Adjacency, Neighbours),
    % the set is independent: node I and each adjacent node are not both in it
    maplist(not_both(Nodes, I), Neighbours),
    % the set is maximal: node I is in it, or one of its adjacent nodes is
    nth1(I, Nodes, Here),
    maplist(in_set_value(Nodes), Neighbours, Values),
    sum([Here|Values], #>=, 1).

% not_both(+Nodes, +I, +J): nodes I and J are not both in the set.
not_both(Nodes, I, J) :-
    nth1(I, Nodes, X),
    nth1(J, Nodes, Y),
    X + Y #=< 1.

% in_set_value(+Nodes, +J, -X): X is 1 when node J is in the set.
in_set_value(Nodes, J, X) :-
    nth1(J, Nodes, X).

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
