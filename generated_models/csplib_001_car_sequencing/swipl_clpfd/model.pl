% csplib_001_car_sequencing: a SWI-Prolog model from DCP Rosetta.
%
% A number of cars are to be produced; they are not identical, because different options are available as variants
% on the basic model. The assembly line has stations which install the options (air-conditioning, sunroof, etc.).
% Each station can handle at most a certain proportion of the cars passing along the line, and cars requiring an
% option must not be bunched together. The cars must be arranged in a sequence so that the capacity of each station
% is never exceeded: for example, if a station can cope with at most half of the cars, at most 1 car in any 2
% requires that option. Each car type is built as often as its demand.
%
% Save this file as model.pl. Download `csplib_001_car_sequencing.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_001_car_sequencing.json')" -t halt model.pl
%
% Data fields: demand (the number of cars of each car type, lists indexed from 0), requires (for each car type, a
% 0/1 value per option: 1 when the car type needs the option), at_most (for each option, the most cars needing it
% allowed in a window), per_slots (for each option, the length of the window).
:- use_module(library(clpfd)).

model(Instance, Vars, [sequence-Sequence]) :-
    Demand = Instance.demand,
    Requires = Instance.requires,
    AtMost = Instance.at_most,
    PerSlots = Instance.per_slots,
    sum_list(Demand, NumCars),
    length(Demand, NumTypes),
    Top is NumTypes - 1,
    numlist(0, Top, Types),
    % Sequence[S] is the car type built in slot S of the line
    length(Sequence, NumCars),
    Sequence ins 0..Top,
    % the number of cars of each type is its demand
    pairs_keys_values(Counts, Types, Demand),
    global_cardinality(Sequence, Counts),
    % Setups[O][S] is 1 when the car in slot S needs option O
    transpose(Requires, RequiresByOption),
    maplist(setups_for(Sequence), RequiresByOption, Setups),
    % in every window of PerSlots[O] consecutive slots, at most AtMost[O] cars need option O
    maplist(windows_ok, Setups, PerSlots, AtMost),
    Vars = [Sequence, Setups].

% the setup of option O in each slot: the requirement of the car type in that slot
setups_for(Sequence, Column, Setups) :-
    maplist(requirement(Column), Sequence, Setups).

requirement(Column, CarType, Setup) :-
    Index #= CarType + 1,
    element(Index, Column, Setup).

% every window of Length consecutive slots holds at most Max setups of the option
windows_ok(Setups, Length, Max) :-
    length(Window, Length),
    append(Window, _, Setups),
    sum(Window, #=<, Max),
    (   Setups = [_|Rest], length(Rest, RestLength), RestLength >= Length
    ->  windows_ok(Rest, Length, Max)
    ;   true
    ).

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
