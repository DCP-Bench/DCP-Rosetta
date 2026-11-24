% csplib_018_water_bucket: a SWI-Prolog model from DCP Rosetta.
%
% You are given an 8 pint bucket full of water, and two empty buckets which hold 5 and 3 pints. Divide the water into
% two by pouring water between the buckets, so that the 8 pint bucket and the 5 pint bucket each end up with 4 pints. A
% transfer pours water from one bucket into another until the first is empty or the second is full. Find the minimum
% number of transfers that reach the goal state.
%
% Save this file as model.pl. Download `csplib_018_water_bucket.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_018_water_bucket.json')" -t halt model.pl
%
% Data fields: capacities (the capacity of each bucket), initial_state (the water in each bucket at the start),
% goal_state (the water in each bucket at the goal), MAX_STEPS (the number of states in the sequence) and
% PADDING_VALUE (the value of each entry of a padded state).
:- use_module(library(clpfd)).

model(Instance, Vars, [cost-Cost, sequence-Seq], min(Cost)) :-
    Caps = Instance.capacities,
    Init = Instance.initial_state,
    Goal = Instance.goal_state,
    get_dict('MAX_STEPS', Instance, Steps),
    get_dict('PADDING_VALUE', Instance, PadV),
    Pad = [PadV, PadV, PadV],
    sum_list(Init, Total),
    max_list(Caps, Max),
    % the states the buckets can be in, and the transitions allowed between them
    all_states(Caps, Total, States),
    transitions(States, Caps, Goal, Pad, Table),
    % Seq[0] is the initial state, and Seq[K] is the state after K transfers, padded after the goal is reached
    Steps1 is Steps - 1,
    length(Rest, Steps1),
    maplist(state_vars(PadV, Max), Rest),
    Seq = [Init|Rest],
    % each state follows from the one before it by a transfer, or is padding once the goal has been reached
    Seq = [_|Tail],
    append(Front, [_], Seq),
    maplist(step(Table), Front, Tail),
    % the cost is the number of transfers: the states after the initial one that are not padding
    maplist(active_flag(PadV), Tail, Acts),
    sum(Acts, #=, Cost),
    % the goal state is reached
    maplist(goal_flag(Goal), Seq, Gs),
    sum(Gs, #>=, 1),
    term_variables([Seq, Acts, Gs, Cost], Vars).

% the states with the given total water, in buckets of the given capacities
all_states([C1, C2, C3], Total, States) :-
    findall([A, B, C], (between(0, C1, A), between(0, C2, B), between(0, C3, C), A + B + C =:= Total), States).

% the table of allowed steps: a transfer from a state, then padding after the goal, and padding stays padding
transitions(States, Caps, Goal, Pad, Table) :-
    findall(Row, (member(S, States), S \== Goal, transfer(Caps, S, T), append(S, T, Row)), Rows),
    append(Goal, Pad, GoalRow),
    append(Pad, Pad, PadRow),
    append(Rows, [GoalRow, PadRow], Table).

% a transfer pours from bucket I into bucket J until I is empty or J is full
transfer(Caps, S, T) :-
    between(1, 3, I),
    between(1, 3, J),
    I =\= J,
    nth1(I, S, SI),
    nth1(J, S, SJ),
    nth1(J, Caps, CJ),
    Amount is min(SI, CJ - SJ),
    Amount > 0,
    findall(V,
            ( nth1(K, S, V0),
              ( K =:= I -> V is V0 - Amount ; K =:= J -> V is V0 + Amount ; V = V0 ) ),
            T).

state_vars(PadV, Max, S) :-
    length(S, 3),
    S ins 0..Max \/ PadV.

step(Table, A, B) :-
    append(A, B, Row),
    tuples_in([Row], Table).

active_flag(PadV, [X|_], B) :-
    B #<==> (X #\= PadV).

goal_flag(Goal, S, B) :-
    S = [A1, A2, A3],
    Goal = [G1, G2, G3],
    B #<==> (A1 #= G1 #/\ A2 #= G2 #/\ A3 #= G3).

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
