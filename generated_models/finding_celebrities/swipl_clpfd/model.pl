% finding_celebrities: a SWI-Prolog model from DCP Rosetta.
%
% Given a list of people at a party and for each person the list of people they know at the party, we want to find the
% celebrities at the party. A celebrity is a person that everybody at the party knows but that only knows other
% celebrities. At least one celebrity is present at the party.
%
% Save this file as model.pl. Download `finding_celebrities.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('finding_celebrities.json')" -t halt model.pl
%
% Data fields: graph (a square 0/1 table, graph[i][j] is 1 when guest i knows guest j, lists indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

model(Instance, Celebrities, [celebrities-Celebrities]) :-
    Graph = Instance.graph,
    length(Graph, N),                  % the number of guests
    length(Celebrities, N),
    % Celebrities[G] is 1 when guest G is a celebrity
    Celebrities ins 0..1,
    % at least one celebrity is present
    sum(Celebrities, #>=, 1),
    Last is N - 1,
    numlist(0, Last, Guests),
    maplist(celebrity_rule(Graph, Celebrities), Guests).

% Guest G is a celebrity exactly when everybody else knows G and G knows only celebrities.
celebrity_rule(Graph, Celebrities, G) :-
    nth0(G, Celebrities, Flag),
    nth0(G, Graph, Knows),             % Knows[K] is 1 when G knows guest K
    length(Graph, N),
    Last is N - 1,
    numlist(0, Last, Ids),
    exclude(==(G), Ids, Others),       % the other guests
    % everybody else knows G
    (   forall(member(I, Others), (nth0(I, Graph, Row), nth0(G, Row, 1)))
    ->  findall(K, (member(K, Others), nth0(K, Knows, 1)), KnownOthers),
        maplist({Celebrities}/[K, CK]>>nth0(K, Celebrities, CK), KnownOthers, KnownFlags),
        length(KnownOthers, NumKnown),
        % G knows only celebrities: every guest G knows is a celebrity
        sum(KnownFlags, #=, CelebritiesKnown),
        Flag #<==> (CelebritiesKnown #= NumKnown)
    ;   Flag #= 0
    ).

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
