% csplib_074_maximum_clique: a SWI-Prolog model from DCP Rosetta.
%
% Given a simple undirected graph G = (V, E), a clique is a subset of vertices V where every two distinct vertices in
% the subset are adjacent (connected by an edge). The maximum clique problem is to find a clique of the largest
% possible size in a given graph.
%
% Save this file as model.pl. Download `csplib_074_maximum_clique.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_074_maximum_clique.json')" -t halt model.pl
%
% Data fields: n (the number of vertices, numbered from 0), adj (the adjacency matrix: adj[I][J] is 1 when vertices
% I and J are joined by an edge, 0 otherwise, indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, [Size|Chosen], [c-Chosen], max(Size)) :-
    N = Instance.n,
    Adj = Instance.adj,
    Last is N - 1,
    % Chosen[I] is 1 when vertex I is in the clique
    length(Chosen, N),
    Chosen ins 0..1,
    % two distinct vertices that are not adjacent cannot both be in the clique
    findall(I-J,
            (between(0, Last, I), between(0, Last, J), I < J,
             nth0(I, Adj, Row), nth0(J, Row, 0)),
            NonEdges),
    maplist({Chosen}/[I-J]>>(nth0(I, Chosen, X), nth0(J, Chosen, Y), X + Y #=< 1), NonEdges),
    % the size of the clique is the number of vertices chosen; maximise it
    sum(Chosen, #=, Size).

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
