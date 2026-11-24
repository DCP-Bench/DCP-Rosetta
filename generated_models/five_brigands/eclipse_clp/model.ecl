% five_brigands: an ECLiPSe model from DCP Rosetta.
%
% The five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, were counting their spoils after a raid, when
% it was found that they had captured altogether exactly 200 doubloons. If Alfonso had twelve times as much, Benito
% three times as much, Carlos the same amount, Diego half as much and Esteban one-third as much, they would still have
% altogether just 200 doubloons. How many doubloons had each? No brigand had less than one doubloon.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% A, B, C, D and E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban.
model(_Instance, [A, B, C, D, E], ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E]) :-
    [A, B, C, D, E] #:: 1..200,

    % they had captured altogether exactly 200 doubloons
    A + B + C + D + E #= 200,

    % with Alfonso's share twelve times as much, Benito's three times as much, Carlos's the same, Diego's half as much
    % and Esteban's one-third as much, the total is still 200 doubloons; multiplied by 6 to keep the coefficients whole
    72*A + 18*B + 6*C + 3*D + 2*E #= 1200,

    % no brigand had less than one doubloon
    A #>= 1, B #>= 1, C #>= 1, D #>= 1, E #>= 1.

% Builds the model, solves it and prints each output.
run :- solve_model([]).

:- lib(branch_and_bound).

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
