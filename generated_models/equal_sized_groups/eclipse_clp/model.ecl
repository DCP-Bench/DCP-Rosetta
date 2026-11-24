% equal_sized_groups: an ECLiPSe model from DCP Rosetta.
%
% Given a sorted list of N elements, divide them into K groups by choosing K-1 split points between them. There
% may be elements with the same value, and elements with the same value must be in the same group. Find K groups
% as close in size to round(N/K) as possible, each group holding at least one element: minimize the total error,
% the sum over the groups of the absolute difference between the group size and round(N/K).
%
% Save this file as model.ecl. Download `equal_sized_groups.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py equal_sized_groups.json
%   eclipse -b model.ecl -e "run('equal_sized_groups_1.dat'), halt"

% Data fields: a (the sorted elements, a list indexed from 0), k (the number of groups).
% A break point is the number of elements before it, so the groups end after elements 1-based positions
% given by the break points.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Breaks, [x-Breaks], min(Total)) :-
    memberchk(a-A, Instance),
    memberchk(k-K, Instance),
    length(A, N),
    % each group should hold round(N/K) elements, the rounding of Python's round
    round_div(N, K, Target),
    % a group can end after element P only when elements P and P+1 have different values
    valid_cuts(A, Cut),
    KM1 is K - 1,
    Last is N - 1,
    length(Breaks, KM1),
    Breaks :: 1..Last,
    (   foreach(B, Breaks), param(Cut) do
        element(B, Cut, 1)
    ),
    % the break points are strictly increasing, so every group holds at least one element
    strictly_increasing(Breaks),
    % the sizes of the groups, from the break points 0, x1, ..., x(K-1), N
    append([0 | Breaks], [N], Bounds),
    group_sizes(Bounds, Sizes),
    % the error of each group against round(N/K)
    (   foreach(S, Sizes), foreach(E, Errors), param(Target) do
        E #= abs(S - Target)
    ),
    % the total error is minimized
    Total #= sum(Errors).

% search: the smallest domain first, the lowest value first
search_goal(Breaks) :-
    search(Breaks, 0, first_fail, indomain_min, complete, []).

% Cut P (from 1 to N-1) is 1 when element P and element P+1 differ, and 0 when they are equal.
valid_cuts([X, Y | T], [Flag | Flags]) :-
    (   X =:= Y -> Flag = 0 ; Flag = 1 ),
    valid_cuts([Y | T], Flags).
valid_cuts([_], []).

strictly_increasing([]).
strictly_increasing([_]).
strictly_increasing([X, Y | T]) :-
    X #< Y,
    strictly_increasing([Y | T]).

% The size of each group, from consecutive bounds.
group_sizes([_], []).
group_sizes([B1, B2 | T], [S | Ss]) :-
    S #= B2 - B1,
    group_sizes([B2 | T], Ss).

% round_div(+N, +K, -T): round(N/K), halves going to the even integer as in Python.
round_div(N, K, T) :-
    Q is N // K,
    R is N mod K,
    D is 2 * R - K,
    (   D < 0 -> T = Q
    ;   D > 0 -> T is Q + 1
    ;   Q mod 2 =:= 0 -> T = Q
    ;   T is Q + 1
    ).

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
