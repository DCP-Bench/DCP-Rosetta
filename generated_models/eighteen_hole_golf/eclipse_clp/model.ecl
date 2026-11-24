% eighteen_hole_golf: an ECLiPSe model from DCP Rosetta.
%
% Generate an 18-hole golf course where each hole has a length of 3, 4, or 5, and the total length of the course
% is 72.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data.

:- lib(ic).

model(_Instance, Holes, [holes-Holes]) :-
    length(Holes, 18),
    % each hole has a length of 3, 4 or 5
    Holes :: 3..5,
    % the total length of the course is 72
    sum(Holes) #= 72.

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
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
