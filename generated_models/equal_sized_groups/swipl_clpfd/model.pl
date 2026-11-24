% equal_sized_groups: a SWI-Prolog model from DCP Rosetta.
%
% I have a sorted list of N elements, and I want to divide them into K groups, by choosing K-1 split points between
% them. There may be elements with the same value, and it is necessary to have items with same value in the same
% group. Find K groups as close in size to round(N/K) as possible. Each group holds at least one element. Choose the
% K-1 break points, where a break point is the number of elements before it, so that the total error is minimized.
% The error of a group is the difference between its size and round(N/K), and the total error is the sum of these.
%
% Save this file as model.pl. Download `equal_sized_groups.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('equal_sized_groups.json')" -t halt model.pl
%
% Data fields: a (the sorted elements, lists indexed from 0), k (the number of groups).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [x-Breaks], min(Error)) :-
    A = Instance.a,                    % the sorted elements
    K = Instance.k,                    % the number of groups
    length(A, N),
    Last is N - 1,
    ideal_size(N, K, Ideal),           % round(N/K)
    % the K-1 break points: Breaks[B] is the number of elements before break B
    NumBreaks is K - 1,
    length(Breaks, NumBreaks),
    Breaks ins 1..Last,
    chain(Breaks, #<),                 % breaks are in increasing order, so every group holds an element
    % a break may not fall between two equal elements
    same_neighbours(A, 1, Forbidden),
    maplist(no_break_at(Forbidden), Breaks),
    % the groups are the gaps between the edges 0, the breaks and N
    append([[0], Breaks, [N]], Edges),
    edge_sizes(Edges, Sizes),
    % the error of each group is its distance from the ideal size, and the total error is minimized
    maplist(deviation(Ideal), Sizes, Deviations),
    sum(Deviations, #=, Error),
    Vars = [Breaks, Error].

% the ideal group size round(N/K), with an exact half going to the even neighbour as Python's round does
ideal_size(N, K, Ideal) :-
    Quotient is N // K,
    Remainder is N mod K,
    (   2*Remainder < K -> Ideal = Quotient
    ;   2*Remainder > K -> Ideal is Quotient + 1
    ;   Quotient mod 2 =:= 0 -> Ideal = Quotient
    ;   Ideal is Quotient + 1
    ).

% Forbidden lists the positions J such that A[J] and A[J+1] are equal, where a break after J elements would split them.
same_neighbours([X, Y|Rest], J, Forbidden) :- !,
    Next is J + 1,
    (   X =:= Y -> Forbidden = [J|Others] ; Forbidden = Others ),
    same_neighbours([Y|Rest], Next, Others).
same_neighbours(_, _, []).

no_break_at(Forbidden, Break) :-
    maplist({Break}/[J]>>(Break #\= J), Forbidden).

% the size of each group is the gap between two consecutive edges
edge_sizes([E1, E2|Rest], [Size|Sizes]) :-
    Size #= E2 - E1,
    edge_sizes([E2|Rest], Sizes).
edge_sizes([_], []).

deviation(Ideal, Size, Deviation) :-
    Deviation #= abs(Size - Ideal).

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
