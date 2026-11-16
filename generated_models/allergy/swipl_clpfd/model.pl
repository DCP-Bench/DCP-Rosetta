% allergy: a SWI-Prolog model from DCP Rosetta.
%
% Four friends (two women named Debra and Janet, and two men named Hugh and Rick) found that each of them is allergic
% to something different: eggs, mold, nuts and ragweed. We would like to match each one's surname (Baxter, Lemon,
% Malone and Fleet) with his or her allergy.
%
% We know that:
%  - Rick is not allergic to mold
%  - Baxter is allergic to eggs
%  - Hugh is neither surnamed Lemon nor Fleet
%  - Debra is allergic to ragweed
%  - Janet (who isn't Lemon) is neither allergic to eggs nor to mold
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

% the friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3; each variable gives the friend with that surname or
% that allergy
model(_Instance, Vars, [baxter-Baxter, eggs-Eggs, fleet-Fleet, lemon-Lemon, malone-Malone, mold-Mold, nuts-Nuts,
                        ragweed-Ragweed]) :-
    Vars = [Baxter, Lemon, Malone, Fleet, Eggs, Mold, Nuts, Ragweed],
    Vars ins 0..3,
    % each surname belongs to exactly one friend
    all_distinct([Baxter, Lemon, Malone, Fleet]),
    % each allergy belongs to exactly one friend
    all_distinct([Eggs, Mold, Nuts, Ragweed]),
    % Rick is not allergic to mold
    Mold #\= 3,
    % Baxter is allergic to eggs
    Baxter #= Eggs,
    % Hugh is neither surnamed Lemon nor Fleet
    Lemon #\= 2,
    Fleet #\= 2,
    % Debra is allergic to ragweed
    Ragweed #= 0,
    % Janet, who isn't Lemon, is neither allergic to eggs nor to mold
    Lemon #\= 1,
    Eggs #\= 1,
    Mold #\= 1.

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
