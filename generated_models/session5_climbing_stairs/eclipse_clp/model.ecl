% session5_climbing_stairs: an ECLiPSe model from DCP Rosetta.
%
% We want to climb a staircase of n steps, taking a number of steps at a time within a range from m1 to m2. For
% example, a staircase of 4 steps with m1 = 1 and m2 = 2 can be climbed with four one-step moves or with two
% two-step moves. Find a way to climb a staircase of n steps in which each move takes between m1 and m2 steps.
% Once the top is reached, the moves take no steps.
%
% Save this file as model.ecl. Download `session5_climbing_stairs.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session5_climbing_stairs.json
%   eclipse -b model.ecl -e "run('session5_climbing_stairs_1.dat'), halt"

% n: the number of steps of the staircase.
% m1, m2: the smallest and the largest number of steps taken in one move.

:- lib(ic).
:- lib(lists).

% Steps: the number of steps taken at each move, 0 when no steps are taken once the top is reached.
model(Instance, Steps, [steps-Steps]) :-
    memberchk(n-N, Instance),
    memberchk(m1-M1, Instance),
    memberchk(m2-M2, Instance),
    % every move that takes steps takes at least one, so N moves are enough
    length(Steps, N),
    % each move takes m1 to m2 steps, or none
    ( foreach(S, Steps), param(M1, M2) do
        S #>= 0,
        S #=< M2,
        NoStep #= (S #= 0),
        Moves #= (S #>= M1),
        NoStep + Moves #>= 1
    ),
    % together the moves climb the N steps of the staircase
    sum(Steps) #= N,
    % once a move takes no steps (the top is reached), every later move takes none
    no_moves_after_top(Steps).

no_moves_after_top([]).
no_moves_after_top([_]).
no_moves_after_top([A, B | Rest]) :-
    StopA #= (A #= 0),
    StopB #= (B #= 0),
    StopA #=< StopB,
    no_moves_after_top([B | Rest]).

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
