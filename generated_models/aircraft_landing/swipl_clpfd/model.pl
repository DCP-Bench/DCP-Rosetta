% aircraft_landing: a SWI-Prolog model from DCP Rosetta.
%
% The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway. Each aircraft
% has a specified time window (earliest and latest possible landing time) and a target landing time. Penalties are
% incurred for landing earlier or later than the target time. Additionally, a minimum separation time between the
% landings of any two aircraft must be respected. This specific problem assumes a fixed landing sequence for the
% aircraft. The objective is to determine the exact landing time for each aircraft to minimize the total penalty,
% while respecting all time windows and separation constraints.
%
% Save this file as model.pl. Download `aircraft_landing.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('aircraft_landing.json')" -t halt model.pl
%
% Data fields: earliest_landing and latest_landing (the time window of each aircraft), target_landing (the target
% landing time of each aircraft), penalty_before and penalty_after (the penalty per unit of time landing before or
% after the target of each aircraft), separation_time (the minimum time between the landings of aircraft I and J,
% a list per aircraft indexed from 0); all lists are indexed from 0.
:- use_module(library(clpfd)).

model(Instance, Vars, [landing_times-Times, total_penalty-Total], min(Total)) :-
    Earliest = Instance.earliest_landing,
    Latest = Instance.latest_landing,
    Target = Instance.target_landing,
    Before = Instance.penalty_before,
    After = Instance.penalty_after,
    Separation = Instance.separation_time,
    length(Earliest, N),
    Last is N - 1,
    % the aircraft are landed in the given order: each pair I < J has I before J
    findall(I-J, (between(0, Last, I), between(0, Last, J), I < J), Pairs),
    % each aircraft lands within its time window
    length(Times, N),
    maplist(landing_window, Earliest, Latest, Times),
    % each aircraft lands at least the separation time after every aircraft before it in the order
    maplist(separated(Separation, Times), Pairs),
    % the penalty of each aircraft for landing before or after its target time
    numlist(0, Last, Indices),
    maplist(penalty(Times, Target, Before, After), Indices, Penalties),
    % the total penalty
    sum(Penalties, #=, Total),
    append([Times, Penalties, [Total]], Vars).

% the landing time lies in the time window of the aircraft
landing_window(Earliest, Latest, Time) :-
    Time in Earliest..Latest.

% the landing of aircraft J comes at least Gap after the landing of aircraft I, where Gap is the separation time of I and J
separated(Separation, Times, I-J) :-
    nth0(I, Times, TimeI),
    nth0(J, Times, TimeJ),
    nth0(I, Separation, Row),
    nth0(J, Row, Gap),
    TimeJ #>= TimeI + Gap.

% the penalty is the early penalty when landing before the target and the late penalty when landing after it
penalty(Times, Target, Before, After, I, Penalty) :-
    nth0(I, Times, Time),
    nth0(I, Target, Tgt),
    nth0(I, Before, Early),
    nth0(I, After, Late),
    Penalty #= max(Early * (Tgt - Time), Late * (Time - Tgt)).

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
