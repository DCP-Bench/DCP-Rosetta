% huey_dewey_louie: an ECLiPSe model from DCP Rosetta.
%
% Huey, Dewey and Louie are being questioned by their uncle. Huey says that Dewey and Louie have an
% equal share in it: if one is guilty, so is the other. Dewey says that if Huey is guilty, then so is
% he. Louie says that Dewey and he are not both guilty. The three cub scouts cannot tell a lie, so all
% three statements are true. The model finds who (if anyone) is guilty.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).
:- lib(listut).

% The model reads no data fields: the guilt of each of the three is the unknown.
% Each guilty flag is 1 when guilty and 0 when not.
model(_Instance, Vars, [huey-Huey, dewey-Dewey, louie-Louie]) :-
    Vars = [Huey, Dewey, Louie],
    Vars :: 0..1,
    % Huey's statement: Dewey and Louie are equally guilty
    Dewey #= Louie,
    % Dewey's statement: if Huey is guilty, then Dewey is guilty
    Huey #=< Dewey,
    % Louie's statement: Dewey and Louie are not both guilty
    Dewey + Louie #=< 1.

:- lib(branch_and_bound).

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
