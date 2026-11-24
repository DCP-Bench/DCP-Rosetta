% cmo_2012: an ECLiPSe model from DCP Rosetta.
%
% Given two positive integers a and b, where a - b is a prime number p and a * b is a perfect square n^2, find the
% smallest value of a that is no less than a given minimum. Also b must be larger than 0, and none of the four values
% a, b, n and p may exceed a given maximum.
%
% Save this file as model.ecl. Download `cmo_2012.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py cmo_2012.json
%   eclipse -b model.ecl -e "run('cmo_2012_1.dat'), halt"
%
% Data fields: max_val is the largest value any of the four numbers may take; min_a is the smallest value allowed for a.
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: a, b, n and p, with a - b = p (prime) and a * b = n * n.
model(Instance, Vars, [a-A, b-B, n-N, p-P], min(A)) :-
    memberchk(max_val-MaxVal, Instance),
    memberchk(min_a-MinA, Instance),
    primes_upto(MaxVal, Primes),
    % a is at least the minimum and at most the maximum
    A #:: MinA..MaxVal,
    % b is positive and at most the maximum
    B #:: 1..MaxVal,
    % n is positive and at most the maximum
    N #:: 1..MaxVal,
    % p is a prime no larger than the maximum
    P #:: Primes,
    % a - b is the prime p
    A - B #= P,
    % a * b is the perfect square n * n
    A * B #= N * N,
    % the smallest a is to be found
    Vars = [A, B, N, P].

% primes_upto(Max, Ps): Ps is the list of the primes up to Max
primes_upto(Max, Ps) :-
    primes_from(2, Max, Ps).

primes_from(I, Max, []) :-
    I > Max, !.
primes_from(I, Max, [I | Ps]) :-
    is_prime(I), !,
    I1 is I + 1,
    primes_from(I1, Max, Ps).
primes_from(I, Max, Ps) :-
    I1 is I + 1,
    primes_from(I1, Max, Ps).

is_prime(N) :-
    N > 1,
    \+ has_divisor(N, 2).

has_divisor(N, D) :-
    D * D =< N,
    (   N mod D =:= 0
    ->  true
    ;   D1 is D + 1,
        has_divisor(N, D1)
    ).

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
