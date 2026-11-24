% session1_five_floors: a SWI-Prolog model from DCP Rosetta.
%
% Baker, Cooper, Fletcher, Miller and Smith live on the first five floors of an apartment house. Baker does not live
% on the fifth floor. Cooper does not live on the first floor. Fletcher does not live on either the fifth or the first
% floor. Miller lives on a higher floor than Cooper. Smith does not live on a floor adjacent to Fletcher's. Fletcher
% does not live on a floor adjacent to Cooper's. They all live on different floors. Find the floors where these people
% live.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Vars holds the floor of each person, B, C, F, M and S (floors numbered 1 to 5).
model(_Instance, Vars, ['B'-B, 'C'-C, 'F'-F, 'M'-M, 'S'-S]) :-
    Vars = [B, C, F, M, S],
    % each person lives on one of the first five floors
    Vars ins 1..5,
    % they all live on different floors
    all_distinct(Vars),
    % Baker does not live on the fifth floor
    B #\= 5,
    % Cooper does not live on the first floor
    C #\= 1,
    % Fletcher does not live on either the fifth or the first floor
    F #\= 5,
    F #\= 1,
    % Miller lives on a higher floor than Cooper
    M #> C,
    % Smith does not live on a floor adjacent to Fletcher's
    abs(S - F) #\= 1,
    % Fletcher does not live on a floor adjacent to Cooper's
    abs(F - C) #\= 1.

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
