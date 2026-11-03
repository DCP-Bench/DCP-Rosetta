:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Divisible by 1 through 9: a ten-digit pandigital number whose first n digits
% form a multiple of n, for every n.
model(_Instance, Vars, [digits-Xs]) :-
    Digits = 10,
    % Xs: the digits of the number, read from left to right
    length(Xs, Digits),
    Xs ins 0..9,
    all_distinct(Xs),
    % Ts: the numbers formed by the first 1, 2, ..., 10 digits
    length(Ts, Digits),
    Upper is 10 ^ Digits,
    Ts ins 0..Upper,
    append(Xs, Ts, Vars),

    numlist(1, Digits, Positions),
    maplist({Xs, Ts}/[I]>>prefix_rule(Xs, Ts, I), Positions).

% The first I digits read as a number, which must divide by I exactly.
prefix_rule(Xs, Ts, I) :-
    length(Front, I),
    append(Front, _, Xs),
    numlist(1, I, Places),
    maplist({I}/[K, Weight]>>(Weight is 10 ^ (I - K)), Places, Weights),
    nth1(I, Ts, T),
    scalar_product(Weights, Front, #=, T),
    T mod I #= 0.
