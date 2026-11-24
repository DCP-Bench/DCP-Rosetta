% session3_people_in_a_room: a SWI-Prolog model from DCP Rosetta.
%
% There are 13 people, 4 of them male. They enter a room one at a time, in a random order. Find an order of entry, of
% males and females, so that the ratio of females to males in the room at any one time is no greater than 7/3.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Seq, [sequence-Seq]) :-
    Total = 13,                            % the number of people
    Males = 4,
    length(Seq, Total),
    Seq ins 0..1,                          % Seq[I] = 1 when the I-th person to enter is female
    Females #= Total - Males,
    sum(Seq, #=, Females),
    numlist(1, Total, Counts),
    % after every entry, with K people in the room and F of them female, 3F =< 7(K - F); with no male in the room the ratio is undefined, so this requires the first person to be male
    maplist(ratio_ok(Seq), Counts).

ratio_ok(Seq, K) :-
    length(Prefix, K),
    append(Prefix, _, Seq),
    sum(Prefix, #=, F),
    3 * F #=< 7 * (K - F).

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
