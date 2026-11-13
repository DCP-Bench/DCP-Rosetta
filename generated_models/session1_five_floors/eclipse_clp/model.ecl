% session1_five_floors: an ECLiPSe model from DCP Rosetta.
%
% Baker, Cooper, Fletcher, Miller, and Smith live on the first five floors of an apartment house. Baker does not live on
% the fifth floor. Cooper does not live on the first floor. Fletcher does not live on either the fifth or the first
% floor. Miller lives on a higher floor than does Cooper. Smith does not live on a floor adjacent to Fletcher's.
% Fletcher does not live on a floor adjacent to Cooper's. They all live on different floors. Find the floors where
% these people live.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% No data fields: the model reads no data, so the run block calls it with an empty list.
:- lib(ic).

% Outputs B, C, F, M, S: the floor of Baker, Cooper, Fletcher, Miller and Smith.
model(_Data, Vars, ['B'-B, 'C'-C, 'F'-F, 'M'-M, 'S'-S]) :-
    Vars = [B, C, F, M, S],
    Vars :: 1..5,

    % they all live on different floors
    alldifferent(Vars),

    % Baker does not live on the fifth floor
    B #\= 5,

    % Cooper does not live on the first floor
    C #\= 1,

    % Fletcher does not live on either the fifth or the first floor
    F #\= 5,
    F #\= 1,

    % Miller lives on a higher floor than does Cooper
    M #> C,

    % Smith does not live on a floor adjacent to Fletcher's
    abs(S - F) #\= 1,

    % Fletcher does not live on a floor adjacent to Cooper's
    abs(F - C) #\= 1.

:- lib(branch_and_bound).

% Solves the model and prints each output.
run :-
    solve_model([]).

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
