% session1_guards_and_apples: a SWI-Prolog model from DCP Rosetta.
%
% A boy wants to give an apple to a girl. To get to her, he has to pass through a number of gates, each with a guard.
% He bribes each guard with half of his apples, plus one. The boy does not have a knife, therefore he gives the guard
% an integer number of apples. After he has given the apple to the girl, he has no apples left, so he has exactly one
% apple after the last gate. Find the number of apples he has before each gate, and after the last gate.
%
% Save this file as model.pl. Download `session1_guards_and_apples.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session1_guards_and_apples.json')" -t halt model.pl
%
% Data fields: num_gates (the number of gates the boy passes through).
:- use_module(library(clpfd)).
:- use_module(library(lists)).

model(Instance, Apples, [apples-Apples]) :-
    NumGates = Instance.num_gates,
    Length is NumGates + 1,
    % Apples[I] is the number of apples before gate I; the last one is the number after the last gate
    length(Apples, Length),
    % the boy never has more than 3 * 2^NumGates apples, the most he can start with
    Top is 3 * 2^NumGates,
    Apples ins 0..Top,
    % exactly one apple is left after the last gate
    last(Apples, AfterLastGate),
    AfterLastGate #= 1,
    % at each gate he gives the guard half his apples plus one
    gates_pass(Apples).

% gates_pass(+Apples): each gate takes half the apples plus one, so the apples before a gate are twice the apples
% after it plus two.
gates_pass([_]).
gates_pass([Before, After|Rest]) :-
    Before #= 2 * (After + 1),
    gates_pass([After|Rest]).

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
