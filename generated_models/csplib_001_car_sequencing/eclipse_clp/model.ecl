% csplib_001_car_sequencing: an ECLiPSe model from DCP Rosetta.
%
% Car sequencing: a number of cars are to be produced; they are not identical, because different options (air
% conditioning, sunroof, etc.) are available as variants on the basic model. The assembly line has stations which
% install the options, and each station is designed to handle at most a certain share of the cars passing along the
% line: at most at_most[o] cars out of any per_slots[o] consecutive cars may require option o. The cars must be
% arranged in a sequence so that the capacity of each station is never exceeded. Find the sequence of car types in
% the assembly line; each car type is a number starting from 0.
%
% Save this file as model.ecl. Download `csplib_001_car_sequencing.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_001_car_sequencing.json
%   eclipse -b model.ecl -e "run('csplib_001_car_sequencing_1.dat'), halt"

% Fields read: demand (the number of cars of each type, indexed from 0), at_most and per_slots (for each option o,
% at most at_most[o] of any per_slots[o] consecutive cars require it), requires (requires[t][o] is 1 when cars of
% type t need option o).
:- lib(gfd).
:- lib(listut).   % nth0/3

% Rank[S] is the rank of the car at position S of the line, a number from 1 to the number of types; the types are
% ranked by decreasing load on the stations, which is the order the search tries them in. Seq[S] is its type.
model(Instance, Rank, [sequence-Seq]) :-
    memberchk(demand-Demand, Instance),
    memberchk(at_most-AtMost, Instance),
    memberchk(per_slots-PerSlots, Instance),
    memberchk(requires-Requires, Instance),
    length(Demand, NTypes),                 % the number of car types
    NCars #= sum(Demand),                   % the length of the line

    % rank the types by decreasing load: the share of each station's capacity that its options use up
    ( foreach(Row, Requires), foreach(D, Demand), count(T, 0, _), foreach(Key-T, Keys),
      param(AtMost, PerSlots) do
        ( foreach(Req, Row), foreach(M, AtMost), foreach(Q, PerSlots), fromto(0, L0, L1, Load) do
            L1 is L0 + Req * Q / M
        ),
        Key is -(Load * 1000 + D)
    ),
    keysort(Keys, Sorted),
    ( foreach(_-T, Sorted), foreach(T, Order) do true ),   % Order[R-1] is the type of rank R

    % each position of the line holds a car of some type
    length(Rank, NCars),
    Rank :: 1..NTypes,
    length(Seq, NCars),
    ( foreach(R, Rank), foreach(S, Seq), param(Order) do
        element(R, Order, S)
    ),

    % exactly demand[t] cars of each type t are produced
    ( foreach(T, Order), count(R, 1, _), param(Demand, Rank) do
        nth0(T, Demand, D),
        occurrences(R, Rank, D)
    ),

    % cars requiring option o must not be bunched together: a station handles at most at_most[o] of any
    % per_slots[o] consecutive cars
    ( foreach(M, AtMost), foreach(Q, PerSlots), count(O, 0, _),
      param(Rank, Requires, Order, Demand, NCars) do
        % Need[S] is 1 when the car at position S requires option O
        ( foreach(T, Order), foreach(Req, Column), param(Requires, O) do
            nth0(T, Requires, Row), nth0(O, Row, Req)
        ),
        length(Need, NCars),
        Need :: 0..1,
        ( foreach(R, Rank), foreach(N, Need), param(Column) do
            element(R, Column, N)
        ),
        sequence(0, M, Q, Need),
        % redundant: the cars needing option O among the first K positions are at most what the station can
        % handle in K positions, and at least the total number needing it minus what fits in the remaining ones
        ( foreach(D, Demand), foreach(Row, Requires), fromto(0, T0, T1, Total), param(O) do
            nth0(O, Row, Req), T1 is T0 + D * Req
        ),
        ( for(K, 1, NCars-1), param(Need, M, Q, NCars, Total) do
            length(Prefix, K), append(Prefix, _, Need),
            Rest is NCars - K,
            Hi is min(Total, (K // Q) * M + min(M, K mod Q)),
            Lo is max(0, Total - ((Rest // Q) * M + min(M, Rest mod Q))),
            Count #= sum(Prefix),
            Count :: Lo..Hi
        )
    ).

% positions from the start of the line, trying the most heavily loading types first
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
