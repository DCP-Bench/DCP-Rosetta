% csplib_013_progressive_party_problem: a SWI-Prolog model from DCP Rosetta.
%
% Timetable a party at a yacht club. Certain boats are designated hosts, and the crews of the remaining boats (the
% guests) in turn visit the host boats for several successive half-hour periods. The crew of a host boat stays on board
% to act as hosts, while the crew of a guest boat visits one host in each period. Every boat can hold a limited number
% of people at a time (its capacity), and crew sizes differ: the total number of people aboard a boat, including the
% host crew and the guest crews, must not exceed its capacity. A guest boat cannot revisit a host, and two guest crews
% cannot meet more than once. Minimise the number of host boats.
%
% Save this file as model.pl. Download `csplib_013_progressive_party_problem.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_013_progressive_party_problem.json')" -t halt model.pl
%
% Data fields: n_boats (the number of boats), n_periods (the number of periods), capacity and crew_size (the capacity
% of each boat and the crew size of each boat, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [visits-Visits, is_host-Hosts], min(Total)) :-
    NBoats = Instance.n_boats,
    NPeriods = Instance.n_periods,
    Capacity = Instance.capacity,
    CrewSize = Instance.crew_size,
    Last is NBoats - 1,
    % Hosts[B] is 1 when boat B is a host, 0 when it is a guest
    length(Hosts, NBoats),
    Hosts ins 0..1,
    % Visits[P][B] is the boat that boat B visits in period P (its own boat when it is a host)
    length(Visits, NPeriods),
    maplist(row_of_length(NBoats), Visits),
    append(Visits, VisitVars),
    VisitVars ins 0..Last,
    % the number of host boats, to minimise
    Total in 0..NBoats,
    sum(Hosts, #=, Total),
    append([Hosts, VisitVars, [Total]], Vars),
    numlist(0, Last, Boats),
    % a host boat stays with its own crew, a guest boat visits another boat, which must be a host
    maplist(visit_rules(Visits, Hosts), Boats),
    % the people aboard a host boat in each period (its crew and the guest crews) stay within its capacity
    maplist(capacity_ok(Visits, Hosts, Capacity, CrewSize, NBoats), Boats),
    % a guest boat never visits the same host in two periods (a host boat has no such rule)
    maplist(distinct_hosts(Visits, Hosts, NPeriods, NBoats), Boats),
    % two crews meet at most once: they are at the same boat in at most one period
    findall(G1-G2, (between(0, Last, G1), I1 is G1 + 1, between(I1, Last, G2)), Pairs),
    maplist(meet_at_most_once(Visits), Pairs),
    % boats with the same capacity and crew size are interchangeable: those chosen as hosts come first
    maplist(identical_first(Hosts, Capacity, CrewSize), Boats),
    % implied: a guest visits NPeriods different hosts, so with any guest there are at least NPeriods hosts
    (Total #< NBoats) #==> (Total #>= NPeriods),
    % implied: in each period all the crews are aboard some host, so the hosts' capacities hold them all
    sum(CrewSize, #=, AllCrew),
    scalar_product(Capacity, Hosts, #>=, AllCrew).

% a boat that is a host is chosen before any later boat with the same capacity and crew size
identical_first(Hosts, Capacity, CrewSize, B) :-
    nth0(B, Hosts, HB),
    nth0(B, Capacity, Cap),
    nth0(B, CrewSize, Crew),
    length(Hosts, NBoats),
    B1 is B + 1,
    numlist(B1, NBoats, Later),            % its last number is no boat: not_after skips it
    maplist(not_after(Hosts, Capacity, CrewSize, HB, Cap, Crew), Later).

not_after(Hosts, Capacity, CrewSize, HB, Cap, Crew, C) :-
    (   nth0(C, Capacity, Cap), nth0(C, CrewSize, Crew)
    ->  nth0(C, Hosts, HC),
        HB #>= HC
    ;   true
    ).

row_of_length(N, Row) :- length(Row, N).

% a host boat visits itself in every period, a guest boat visits a different boat, which must be a host
visit_rules(Visits, Hosts, B) :-
    nth0(B, Hosts, HB),
    maplist(visit_rule(Hosts, B, HB), Visits).

visit_rule(Hosts, B, HB, Row) :-
    nth0(B, Row, V),
    V1 #= V + 1,
    element(V1, Hosts, 1),
    (HB #= 1) #==> (V #= B),
    (HB #= 0) #==> (V #\= B).

% the people aboard boat B in each period, when it is a host (its own crew and the guest crews visiting it),
% stay within its capacity
capacity_ok(Visits, Hosts, Capacity, CrewSize, NBoats, B) :-
    nth0(B, Hosts, HB),
    nth0(B, Capacity, Cap),
    nth0(B, CrewSize, Crew),
    Max is NBoats - 1,
    findall(G, (between(0, Max, G), G =\= B), Guests),
    maplist(crew_of(CrewSize), Guests, Cs),
    maplist(period_capacity(B, HB, Cap, Crew, Guests, Cs), Visits).

crew_of(CrewSize, G, C) :- nth0(G, CrewSize, C).

period_capacity(B, HB, Cap, Crew, Guests, Cs, Row) :-
    maplist(visits_boat(Row, B), Guests, Bs),
    scalar_product([Crew|Cs], [HB|Bs], #=<, Cap).

% guest G visits boat B in the period of Row
visits_boat(Row, B, G, F) :-
    nth0(G, Row, V),
    F #<==> (V #= B).

% guest boat B never visits a host twice
distinct_hosts(Visits, Hosts, NPeriods, NBoats, B) :-
    nth0(B, Hosts, HB),
    maplist(nth0(B), Visits, Vs),
    numlist(1, NPeriods, Periods),
    maplist(shifted(HB, NBoats), Periods, Vs, Ws),
    all_distinct(Ws).

% a host's entries are made different by shifting them by their period, so only a guest's visits must differ
shifted(HB, NBoats, P, V, W) :-
    W #= V + HB * P * NBoats.

meet_at_most_once(Visits, G1-G2) :-
    maplist(same_visit(G1, G2), Visits, Same),
    sum(Same, #=<, 1).

same_visit(G1, G2, Row, S) :-
    nth0(G1, Row, V1), nth0(G2, Row, V2),
    S #<==> (V1 #= V2).

% labelling picks the variable with the smallest domain, breaking ties by the most constraints (ffc)
labeling_options([ffc, down]).

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
