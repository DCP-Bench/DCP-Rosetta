% cabling: a SWI-Prolog model from DCP Rosetta.
%
% A rack cabinet holds a number of 1U devices, such as servers and routers. Some devices must be connected by several
% cables. Each device takes one position in the rack, and neighbouring positions are one unit apart. A cable between two
% devices is as long as the distance between their positions, so connecting them by k cables costs k times that
% distance. Place the devices so that the sum of all cable lengths is as short as possible.
%
% Save this file as model.pl. Download `cabling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('cabling.json')" -t halt model.pl
%
% Data fields: n (the number of devices and of rack positions), devices (the names of the devices), cable_struct (one
% row per connection: the names of its two devices, then the number of cables between them).
:- use_module(library(clpfd)).

model(Instance, Vars, [final_sum-Sum], min(Sum)) :-
    N = Instance.n,
    Devices = Instance.devices,
    Cables = Instance.cable_struct,
    Last is N - 1,
    % Positions[D]: the rack position of device D (devices in the order of the list), counted from 0
    length(Positions, N),
    Positions ins 0..Last,
    all_distinct(Positions),                % one device to each position
    % each connection costs its number of cables times the distance between its devices
    maplist(cable_length(Devices, Positions), Cables, Lengths),
    sum(Lengths, #=, Sum),                  % the total cable length, to be made as short as possible
    append([Positions, Lengths, [Sum]], Vars).

% Length is the total length of the cables of one connection between the two named devices.
cable_length(Devices, Positions, [NameA, NameB, Count], Length) :-
    once(nth0(A, Devices, NameA)),
    once(nth0(B, Devices, NameB)),
    nth0(A, Positions, PosA),
    nth0(B, Positions, PosB),
    Length #= abs(PosA - PosB) * Count.

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
