% added_corners: an ECLiPSe model from DCP Rosetta.
%
% Enter the digits 1 through 8 into the eight positions around the edge of a 3 by 3 grid whose centre is empty, using
% each digit exactly once. The corners are circles and the middles of the sides are squares:
%
%   C F C
%   F   F
%   C F C
%
% The number in each square must equal the sum of the numbers in the two circles adjoining it. Find the values of the
% positions, starting from the top left corner and moving like reading a book: left to right, top to bottom.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
% Positions are numbered in reading order: P0 top left, P1 top middle, P2 top right, P3 middle left, P4 middle right,
% P5 bottom left, P6 bottom middle, P7 bottom right.
:- lib(ic).

model(_Instance, Ps, [positions-Ps]) :-
    Ps = [P0, P1, P2, P3, P4, P5, P6, P7],
    % the eight positions hold the digits 1 through 8, each exactly once
    Ps :: 1..8,
    alldifferent(Ps),
    % the middle of the top side is the sum of the two top corners
    P1 #= P0 + P2,
    % the middle of the left side is the sum of the two left corners
    P3 #= P0 + P5,
    % the middle of the right side is the sum of the two right corners
    P4 #= P2 + P7,
    % the middle of the bottom side is the sum of the two bottom corners
    P6 #= P5 + P7.

:- lib(branch_and_bound).

% Reads nothing, builds the model, solves it and prints each output.
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
