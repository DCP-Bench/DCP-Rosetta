% three_coins: an ECLiPSe model from DCP Rosetta.
%
% Three coins lie on a table in the order tails, heads, tails. In precisely three moves, make them all face
% heads or all face tails. Each move consists of choosing one coin and flipping it over.
%
% Save this file as model.ecl. Download `three_coins.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py three_coins.json
%   eclipse -b model.ecl -e "run('three_coins_1.dat'), halt"

% init: the starting faces of the three coins, 1 for tails and 0 for heads.
% num_moves: the number of moves.

:- lib(ic).
:- lib(lists).

% Steps: the faces of the three coins before the first move and after each move, 1 for tails and 0 for heads.
model(Instance, Vars, [steps-Steps]) :-
    memberchk(init-Init, Instance),
    memberchk(num_moves-Moves, Instance),
    NumConfigs is Moves + 1,
    length(Steps, NumConfigs),
    Steps = [Init | _],                   % the first configuration is the starting one
    ( foreach(Config, Steps) do
        length(Config, 3),
        Config :: 0..1
    ),
    % each move flips exactly one coin
    one_coin_per_move(Steps),
    % at the end all three coins face the same way
    final_config(Steps, [First | Others]),
    ( foreach(C, Others), param(First) do
        C #= First
    ),
    append(Steps, Vars).

% Last is the last configuration of the list Steps
final_config([Last], Last).
final_config([_ | Rest], Last) :-
    final_config(Rest, Last).

% each move, from one configuration to the next, changes the face of exactly one coin
one_coin_per_move([_]).
one_coin_per_move([Before, After | Rest]) :-
    ( foreach(B, Before), foreach(A, After), foreach(D, Diffs) do
        D #= (B #\= A)
    ),
    sum(Diffs) #= 1,
    one_coin_per_move([After | Rest]).

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
