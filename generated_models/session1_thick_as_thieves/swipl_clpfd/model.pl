% session1_thick_as_thieves: a SWI-Prolog model from DCP Rosetta.
%
% Following a robbery at Sparkles the Jeweller's, Inspector Korner of the Yard interviewed six of the usual suspects.
% He knew that the getaway car had been barely big enough to hold two, so he reckoned that at least four of them were
% innocent. He also supposed that the innocent ones would tell the truth, while the guilty one or ones would lie. What
% they actually said was:
%   Artie: "It wasn't me."
%   Bill: "Crackitt was in it up to his neck."
%   Crackitt: "No I wasn't."
%   Dodgy: "If Crackitt did it, Bill did it with him."
%   Edgy: "Nobody did it alone."
%   Fingers: "That's right: it was Artie and Dodgy together."
% If the good inspector's suppositions were correct, who is guilty?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Vars holds one 0/1 value per suspect, 1 when that suspect is guilty: Artie, Bill, Crackitt, Dodgy, Edgy, Fingers.
model(_Instance, Vars, [artie-Artie, bill-Bill, crackitt-Crackitt, dodgy-Dodgy,
                        edgy-Edgy, fingers-Fingers]) :-
    Vars = [Artie, Bill, Crackitt, Dodgy, Edgy, Fingers],
    Vars ins 0..1,
    % the getaway car held at most two, so at most two are guilty (at least four are innocent)
    sum(Vars, #=, Guilty),
    Guilty #=< 2,
    % a suspect is guilty exactly when the statement he made is false (the innocent tell the truth)
    % Artie: "It wasn't me."
    guilty_iff_false(Artie, #\ Artie),
    % Bill: "Crackitt was in it up to his neck."
    guilty_iff_false(Bill, Crackitt),
    % Crackitt: "No I wasn't."
    guilty_iff_false(Crackitt, #\ Crackitt),
    % Dodgy: "If Crackitt did it, Bill did it with him."
    guilty_iff_false(Dodgy, Crackitt #==> Bill),
    % Edgy: "Nobody did it alone." is false only when exactly one is guilty
    guilty_iff_false(Edgy, Guilty #\= 1),
    % Fingers: "That's right: it was Artie and Dodgy together."
    guilty_iff_false(Fingers, Artie #/\ Dodgy).

% guilty_iff_false(?Guilty, +Statement): Guilty is 1 exactly when Statement is false.
guilty_iff_false(Guilty, Statement) :-
    Guilty #<==> #\ Statement.

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
