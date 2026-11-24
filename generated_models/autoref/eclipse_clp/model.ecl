% autoref: an ECLiPSe model from DCP Rosetta.
%
% Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S = (s0, s1, ..., sn, sn+1) of integers
% between 0 and n such that there are si occurrences of i in S for each integer i from 0 to n, and sn+1 = m.
%
% Save this file as model.ecl. Download `autoref.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py autoref.json
%   eclipse -b model.ecl -e "run('autoref_1.dat'), halt"

% Fields read: n is the integer n (the series has n+2 terms), m is the integer m (the value of the last term).

:- lib(ic).
:- lib(listut).

% Output s: the series S, its terms s0 to sn+1 in order.
model(Instance, S, [s-S]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    Length is N + 2,
    length(S, Length),
    % every term is between 0 and n
    S :: 0..N,

    % the last term sn+1 is m
    Last is N + 1,
    nth0(Last, S, SLast),
    SLast #= M,

    % for each i from 0 to n, there are si occurrences of i in S
    ( for(I, 0, N), param(S) do
        nth0(I, S, Si),
        ( foreach(Xj, S), foreach(B, Bs), param(I) do
            B #= (Xj #= I)
        ),
        sum(Bs) #= Si
    ).

% the search picks the term with the fewest candidate values first and tries the lowest value first
search_goal(S) :-
    search(S, 0, first_fail, indomain_min, complete, []).

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
