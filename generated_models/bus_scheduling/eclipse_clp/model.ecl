% bus_scheduling: an ECLiPSe model from DCP Rosetta.
%
% A city considers a mass-transit bus system to reduce in-city driving, and wants the minimum number of buses that meets the
% transportation needs through the day. The demand for buses is approximated as constant over successive 4-hour intervals.
% Each bus can operate only 8 successive hours a day, so a bus that starts in one interval also works in the next one. The
% day is cyclic: the first interval follows the last. The number of buses available in each interval, those starting in it
% and those that started in the interval before, must meet the demand for that interval. Find the minimum number of buses,
% and how many start in each time slot.
%
% Save this file as model.ecl. Download `bus_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py bus_scheduling.json
%   eclipse -b model.ecl -e "run('bus_scheduling_1.dat'), halt"

% Fields read: demands is the number of buses needed in each 4-hour interval, indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Output x: the number of buses that start in each time slot, in order.
model(Instance, Xs, [x-Xs], min(sum(Xs))) :-
    memberchk(demands-Demands, Instance),
    length(Demands, N),
    length(Xs, N),
    % the total demand is an upper bound for the buses that start in one slot
    ( foreach(D, Demands), fromto(0, A, B, Total) do B is A + D ),
    Xs :: 0..Total,
    % the buses available in slot I are those starting in slot I and in the slot before it (the day is cyclic)
    ( for(I, 1, N), param(Xs, Demands, N) do
        nth1(I, Demands, Demand),
        Previous is (I + N - 2) mod N + 1,
        nth1(I, Xs, XI),
        nth1(Previous, Xs, XPrevious),
        XI + XPrevious #>= Demand
    ).
    % the objective is the total number of buses, to be as small as possible

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
