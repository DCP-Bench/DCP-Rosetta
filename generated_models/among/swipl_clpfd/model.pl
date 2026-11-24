% among: a SWI-Prolog model from DCP Rosetta.
%
% Find an array x of n integers between 0 and 7, inclusive, such that exactly m of them take one of the values in v.
% The other elements may take any other value in that range.
%
% Save this file as model.pl. Download `among.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('among.json')" -t halt model.pl
%
% Data fields: m (the number of elements of x that take one of the values in v), n (the number of elements of x),
% v (the values, a list indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-X]) :-
    Values = Instance.v,
    N = Instance.n,
    Count = Instance.m,
    length(X, N),
    % each element is between 0 and 7
    X ins 0..7,
    % Hits[I] is 1 when element I takes one of the values in v
    length(Hits, N),
    Hits ins 0..1,
    maplist(takes_one_of(Values), X, Hits),
    % exactly m elements take one of the values in v
    sum(Hits, #=, Count),
    append([X, Hits], Vars).

% Hit is 1 exactly when X equals one of the Values
takes_one_of(Values, X, Hit) :-
    maplist(equal_flag(X), Values, Flags),
    sum(Flags, #=, Matches),
    Hit #<==> (Matches #>= 1).

% Flag is 1 when X equals Value
equal_flag(X, Value, Flag) :-
    Flag #<==> (X #= Value).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
