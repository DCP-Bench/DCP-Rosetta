% csplib_016_traffic_lights: an ECLiPSe model from DCP Rosetta.
%
% Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are for vehicles, and four
% (P1 to P4) are for pedestrians. The lights have different states. The combinations of light states
% (V_i, P_i, V_{i+1}, P_{i+1}) that are safe for intersecting roads are listed, for i = 1 to 4 with V_5 = V_1 and
% P_5 = P_1; every other combination is disallowed to prevent accidents. Vehicle light states: 0 = red, 1 = red-yellow,
% 2 = green, 3 = yellow. Pedestrian light states: 0 = red, 1 = green.
%
% Save this file as model.ecl. Download `csplib_016_traffic_lights.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_016_traffic_lights.json
%   eclipse -b model.ecl -e "run('csplib_016_traffic_lights_1.dat'), halt"

% Instance field: allowed_tuples, the safe combinations of four states (V_i, P_i, V_{i+1}, P_{i+1}), one list per
% combination, indexed from 0 as in the JSON.
% Output lights: [V1, V2, V3, V4, P1, P2, P3, P4].

:- lib(ic).
:- lib(ic_mdd).

model(Instance, Vars, [lights-Vars]) :-
    memberchk(allowed_tuples-Safe, Instance),
    Vars = [V1, V2, V3, V4, P1, P2, P3, P4],
    % vehicle lights take the states 0 to 3, pedestrian lights the states 0 and 1
    [V1, V2, V3, V4] :: 0..3,
    [P1, P2, P3, P4] :: 0..1,
    % for each pair of intersecting roads, the states of the two lights must be one of the safe combinations
    % (V5 = V1 and P5 = P1, so the last road wraps around to the first)
    table([[V1, P1, V2, P2]], Safe),
    table([[V2, P2, V3, P3]], Safe),
    table([[V3, P3, V4, P4]], Safe),
    table([[V4, P4, V1, P1]], Safe).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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
