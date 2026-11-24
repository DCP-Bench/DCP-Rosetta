% wolf_goat_cabbage: an ECLiPSe model from DCP Rosetta.
%
% The wolf, goat and cabbage problem is a river crossing puzzle. A farmer with a wolf, a goat, and a cabbage must cross
% a river by boat. The boat can carry only the farmer and a single item. If left unattended together, the wolf would
% eat the goat, or the goat would eat the cabbage. How can they cross the river without anything being eaten? The
% crossing takes the given number of stages. At the first stage everything is on the starting shore, at the last stage
% everything is on the destination shore, and the boat, with the farmer, changes shore from each stage to the next.
%
% Save this file as model.ecl. Download `wolf_goat_cabbage.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py wolf_goat_cabbage.json
%   eclipse -b model.ecl -e "run('wolf_goat_cabbage_1.dat'), halt"

% Data fields: stage (the number of stages of the crossing).
% Outputs: wolf_pos, goat_pos, cabbage_pos and boat_pos give, for each stage in order, 1 when the item (or the boat)
% is on the destination shore and 0 when it is on the starting shore.
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [wolf_pos-Wolf, goat_pos-Goat, cabbage_pos-Cabbage, boat_pos-Boat]) :-
    memberchk(stage-Stages, Instance),
    length(Wolf, Stages),
    length(Goat, Stages),
    length(Cabbage, Stages),
    length(Boat, Stages),
    Wolf :: 0..1, Goat :: 0..1, Cabbage :: 0..1, Boat :: 0..1,
    % at the first stage everything is on the starting shore
    ( foreach(Shore, [Wolf, Goat, Cabbage, Boat]) do Shore = [First|_], First #= 0 ),
    % at the last stage everything is on the destination shore
    ( foreach(Shore, [Wolf, Goat, Cabbage, Boat]), param(Stages) do
        nth1(Stages, Shore, Last), Last #= 1
    ),
    % at each stage the wolf would eat the goat, or the goat the cabbage, unless the farmer is on the same shore
    ( for(T, 1, Stages), param(Wolf, Goat, Cabbage, Boat) do
        nth1(T, Wolf, W), nth1(T, Goat, G), nth1(T, Cabbage, C), nth1(T, Boat, B),
        WolfGoatTogether #= (W #= G), FarmerAway1 #= (B #\= W),
        WolfGoatTogether + FarmerAway1 #=< 1,
        GoatCabbageTogether #= (G #= C), FarmerAway2 #= (B #\= G),
        GoatCabbageTogether + FarmerAway2 #=< 1
    ),
    % from each stage to the next the boat changes shore, carrying the farmer and at most one item
    ( for(T, 1, Stages-1), param(Wolf, Goat, Cabbage, Boat) do
        T1 is T + 1,
        nth1(T, Boat, B0), nth1(T1, Boat, B1),
        B1 #\= B0,
        ( foreach(Item, [Wolf, Goat, Cabbage]), foreach(Moved, Moves), param(T, T1, B0) do
            nth1(T, Item, I0), nth1(T1, Item, I1),
            Moved #= (I1 #\= I0),
            % an item can only cross from the shore the boat is on
            OffBoat #= (I0 #\= B0),
            Moved + OffBoat #=< 1
        ),
        sum(Moves) #=< 1
    ),
    join_lists(Wolf, Goat, WG),
    join_lists(WG, Cabbage, WGC),
    join_lists(WGC, Boat, Vars).

join_lists([], L, L).
join_lists([X|Xs], L, [X|Ys]) :-
    join_lists(Xs, L, Ys).

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
