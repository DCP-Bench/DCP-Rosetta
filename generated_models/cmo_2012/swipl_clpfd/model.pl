% cmo_2012: a SWI-Prolog model from DCP Rosetta.
%
% Find two positive integers a and b such that a - b is a prime number p and a * b is a perfect square n^2, with a
% no smaller than a given minimum and b larger than 0. None of a, b, n and p may exceed a given maximum. Take the
% smallest such a.
%
% Save this file as model.pl. Download `cmo_2012.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('cmo_2012.json')" -t halt model.pl
%
% Data fields: min_a (the smallest value allowed for a), max_val (the largest value allowed for each of a, b, n and
% p).
:- use_module(library(clpfd)).

model(Instance, Vars, [a-A, b-B, n-N, p-P], min(A)) :-
    MinA = Instance.min_a,
    MaxVal = Instance.max_val,
    % p is a prime; since b >= 1, p = a - b is at most MaxVal - 1, so only the primes below MaxVal need be listed
    Limit is MaxVal - 1,
    findall(Prime, (between(2, Limit, Prime), is_prime(Prime)), Primes),
    domain_of_numbers(Primes, PrimeDomain),
    A in MinA..MaxVal,
    B in 1..MaxVal,
    N in 0..MaxVal,
    P in PrimeDomain,
    % the difference a - b is the prime p
    P #= A - B,
    % the product a * b is the square n^2: the pair (n, a * b) is read from the table of squares of 0..max_val,
    % which is much cheaper to propagate than the product of two variables equated with a square
    MaxProduct is MaxVal * MaxVal,
    Product in 0..MaxProduct,
    A * B #= Product,
    findall([K, KK], (between(0, MaxVal, K), KK is K * K), Squares),
    tuples_in([[N, Product]], Squares),
    Vars = [A, B, P, N, Product].

% the clpfd domain made of the given numbers
domain_of_numbers([Number], Number).
domain_of_numbers([Number, Next|Numbers], Number \/ Domain) :-
    domain_of_numbers([Next|Numbers], Domain).

% a number is prime when it is at least 2 and no number from 2 up to its square root divides it
is_prime(N) :-
    N >= 2,
    Root is floor(sqrt(N)),
    \+ ( between(2, Root, D), N mod D =:= 0 ).

% a is labelled first, from its smallest value up, then b, p and n follow
labeling_options([leftmost]).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
