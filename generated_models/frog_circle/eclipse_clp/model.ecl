% frog_circle: an ECLiPSe model from DCP Rosetta.
%
% Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then jumps to the card 1 place clockwise around
% the circle. Then, from card k, it jumps directly to the card k places clockwise around the circle. The frog continues
% jumping in this way forever. Find an arrangement of cards that allows the frog to jump on every card starting from
% card 1: a list of n different integers, each from 1 to n.
%
% Save this file as model.ecl. Download `frog_circle.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py frog_circle.json
%   eclipse -b model.ecl -e "run('frog_circle_1.dat'), halt"
%
% The data fields: n is the number of cards.

:- lib(ic).

% X[P] is the card at position P (positions 1 to N clockwise). Succ[P] is the position the frog lands on after a jump
% from position P, and Pos[K] is the position the frog is on at its K-th visit.
model(Instance, Vars, [x-X], none) :-
    memberchk(n-N, Instance),
    length(X, N),
    X :: 1..N,
    alldifferent(X),

    % rotating the circle keeps an arrangement valid, so card 1 can be fixed at position 1 without losing solutions
    X = [1 | _],

    % the frog jumps X[P] places clockwise from position P, wrapping around the circle of N positions
    length(Succ, N),
    Succ :: 1..N,
    ( foreach(Xp, X), foreach(Sp, Succ), count(P, 1, _), param(N) do
        Wrap #= (Xp + P #> N),
        Sp #= Xp + P - N * Wrap
    ),

    % the frog starts on card 1 (position 1) and each visit is the successor of the one before
    length(Pos, N),
    Pos :: 1..N,
    alldifferent(Pos),
    Pos = [Pos1 | _],
    element(Pos1, X, 1),
    chain(Pos, Succ),

    % the frog reaches every card, since its first N visits are all different positions
    append(X, Succ, Aux),
    append(Aux, Pos, Vars).

% chain(+Pos, +Succ): each position in Pos is the successor of the one before it
chain([_], _).
chain([P, Q | T], Succ) :-
    element(P, Succ, Q),
    chain([Q | T], Succ).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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
