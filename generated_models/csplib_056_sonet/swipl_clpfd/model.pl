% csplib_056_sonet: a SWI-Prolog model from DCP Rosetta.
%
% In the SONET problem, we are given a set of nodes and the traffic demand for each pair of nodes. The nodes are
% connected by a set of rings. A node is installed on a ring using an add-drop multiplexer (ADM). For two nodes to
% communicate, they must be on at least one common ring. Each ring has a capacity, limiting the number of nodes it
% can host. The objective is to satisfy all communication demands while minimizing the total number of ADMs used.
%
% Save this file as model.pl. Download `csplib_056_sonet.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_056_sonet.json')" -t halt model.pl
%
% Data fields: n (the number of nodes), r (the number of rings), capacity_nodes (the number of nodes each ring can
% host, lists indexed from 0), demand (the traffic demand from node I to node J, a matrix indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, [TotalAdms|Cells], [ring_config-Rings, total_adms-TotalAdms], min(TotalAdms)) :-
    NumRings = Instance.r,
    N = Instance.n,
    Demand = Instance.demand,
    Capacity = Instance.capacity_nodes,
    % Rings[K][I] = 1 when node I is on ring K
    length(Rings, NumRings),
    maplist({N}/[Ring]>>(length(Ring, N), Ring ins 0..1), Rings),
    % each ring hosts no more nodes than its capacity
    maplist([Ring, Cap]>>sum(Ring, #=<, Cap), Rings, Capacity),
    Last is N - 1,
    % every two nodes that have traffic between them (in either direction) share a ring
    findall(I-J,
            (between(0, Last, I), between(0, Last, J), I < J,
             nth0(I, Demand, RowI), nth0(J, Demand, RowJ),
             nth0(J, RowI, Forward), nth0(I, RowJ, Backward),
             Forward + Backward > 0),
            Pairs),
    maplist({Rings}/[I-J]>>shared_ring(Rings, I, J), Pairs),
    % one ADM for each node installed on a ring: the total is the number of ones in all the rings
    append(Rings, Cells),
    sum(Cells, #=, TotalAdms).

% the two nodes I and J are on a common ring
shared_ring(Rings, I, J) :-
    maplist({I, J}/[Ring, Both]>>(nth0(I, Ring, Here), nth0(J, Ring, There), Both #= min(Here, There)),
            Rings, Shared),
    sum(Shared, #>=, 1).

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
