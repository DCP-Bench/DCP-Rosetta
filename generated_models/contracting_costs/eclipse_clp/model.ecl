% contracting_costs: an ECLiPSe model from DCP Rosetta.
%
% A contractor planning the construction of a house finds that he has to pay: $1,100 to the paper hanger and the
% painter; $1,700 to the painter and the plumber; $1,100 to the plumber and the electrician; $3,300 to the electrician
% and the carpenter; $5,300 to the carpenter and the mason; and $3,200 to the mason and the painter. Find what each man
% charges for his services.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"
%
% This problem has no data fields: the payments above are part of the model.
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: the charge of each tradesman in dollars.
model(_Instance, [PaperHanger, Painter, Plumber, Electrician, Carpenter, Mason],
      [paper_hanger-PaperHanger, painter-Painter, plumber-Plumber, electrician-Electrician,
       carpenter-Carpenter, mason-Mason]) :-
    % each charge is a non-negative amount, and (to give a finite domain for labelling) at most 10000
    [PaperHanger, Painter, Plumber, Electrician, Carpenter, Mason] :: 0..10000,
    % the paper hanger and the painter together: 1100
    PaperHanger + Painter #= 1100,
    % the painter and the plumber together: 1700
    Painter + Plumber #= 1700,
    % the plumber and the electrician together: 1100
    Plumber + Electrician #= 1100,
    % the electrician and the carpenter together: 3300
    Electrician + Carpenter #= 3300,
    % the carpenter and the mason together: 5300
    Carpenter + Mason #= 5300,
    % the mason and the painter together: 3200
    Mason + Painter #= 3200.

run :- solve_model([]).

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
