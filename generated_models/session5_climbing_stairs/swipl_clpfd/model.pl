% session5_climbing_stairs: a SWI-Prolog model from DCP Rosetta.
%
% We want to climb a stair of n steps, taking a number of steps at a time within a given range [m1, m2]. For example,
% a stair of 4 steps with m1 = 1 and m2 = 2 can be climbed with four one-step moves or with two two-step moves. Find a
% way to climb a stair of n steps, where each move takes between m1 and m2 steps.
%
% Save this file as model.pl. Download `session5_climbing_stairs.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session5_climbing_stairs.json')" -t halt model.pl
%
% Data fields: n (the number of steps of the stair), m1 and m2 (the smallest and largest number of steps per move).
:- use_module(library(clpfd)).

model(Instance, Steps, [steps-Steps]) :-
    N = Instance.n,
    Lo = Instance.m1,
    Hi = Instance.m2,
    length(Steps, N),                      % at most one move per step; moves after the top of the stair are 0
    Steps ins 0..Hi,
    % the moves together climb exactly the n steps
    sum(Steps, #=, N),
    % each move is either 0 or between m1 and m2 steps
    maplist(move_ok(Lo, Hi), Steps),
    % once a move is 0 (the top is reached), every later move is 0
    zeros_at_end(Steps).

move_ok(Lo, Hi, Move) :-
    Move #= 0 #\/ (Move #>= Lo #/\ Move #=< Hi).

zeros_at_end([]).
zeros_at_end([_]).
zeros_at_end([Move, Next|Rest]) :-
    (Move #= 0) #==> (Next #= 0),
    zeros_at_end([Next|Rest]).

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
