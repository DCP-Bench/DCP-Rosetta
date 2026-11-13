% csplib_007_all_interval: an ECLiPSe model from DCP Rosetta.
%
% All-interval series: given n, find a series s = (s_1, ..., s_n) such that s is a permutation of
% 0, 1, ..., n-1, and the interval vector v = (|s_2 - s_1|, |s_3 - s_2|, ..., |s_n - s_(n-1)|) is
% a permutation of 1, 2, ..., n-1. Each of the intervals from 1 to n-1 occurs between some pair
% of neighbouring elements of the series, exactly once.
%
% Save this file as model.ecl. Download `csplib_007_all_interval.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_007_all_interval.json
%   eclipse -b model.ecl -e "run('csplib_007_all_interval_1.dat'), halt"

% Field read from the data: n (the number of pitch classes, and the length of the series).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['x'-X, 'diffs'-Diffs]) :-
    memberchk(n-N, Instance),
    Last is N - 1,
    % the series x is a permutation of the pitch classes 0 to n-1
    length(X, N),
    X :: 0..Last,
    alldifferent(X),
    % the intervals between neighbouring pitch classes are a permutation of 1 to n-1
    length(Diffs, Last),
    Diffs :: 1..Last,
    alldifferent(Diffs),
    ( for(I, 1, Last), param(X, Diffs) do
        I1 is I + 1,
        nth1(I, X, Before),
        nth1(I1, X, After),
        nth1(I, Diffs, Interval),
        % the interval between two neighbours is the absolute difference of their pitch classes
        Interval #= abs(After - Before)
    ),
    append(X, Diffs, Vars).

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
