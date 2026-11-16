% huey_dewey_louie: a SWI-Prolog model from DCP Rosetta.
%
% Huey, Dewey and Louie are being questioned by their uncle. Huey says: Dewey and Louie have an equal share in it;
% if one is guilty, so is the other. Dewey says: if Huey is guilty, then so am I. Louie says: Dewey and I are not
% both guilty. The uncle knows that they are cub scouts, so they cannot tell a lie. Has he got sufficient
% information to decide who (if any) are guilty? Each of the three is either guilty (1) or not guilty (0).
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% Data fields: none, the problem has no data; the model reads nothing from the instance.
:- use_module(library(clpfd)).

model(_Instance, Vars, [huey-Huey, dewey-Dewey, louie-Louie]) :-
    Vars = [Huey, Dewey, Louie],
    Vars ins 0..1,
    % Huey's statement is true: Dewey and Louie are both guilty or both innocent
    Dewey #<==> Louie,
    % Dewey's statement is true: if Huey is guilty, then Dewey is guilty too
    Huey #==> Dewey,
    % Louie's statement is true: Dewey and Louie are not both guilty
    #\ (Dewey #/\ Louie).

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
