% frog_circle: a SWI-Prolog model from DCP Rosetta.
%
% Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then jumps to the card 1 place
% clockwise around the circle. Then, from card k, he jumps directly to the card k places clockwise around
% the circle. The frog continues jumping in this way forever.
%
% Find an arrangement of cards that allows the frog to jump on every card starting from card 1.
%
% Save this file as model.pl. Download `frog_circle.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('frog_circle.json')" -t halt model.pl
%
% Data fields: n (the number of cards).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-X]) :-
    N = Instance.n,
    Last is N - 1,
    % X[P] is the card at place P of the circle (places 0 to n-1 clockwise, listed from card 1): n different cards
    % from 1 to n
    length(X, N),
    X ins 1..N,
    all_different(X),
    X = [1|_],                             % symmetry breaking: the circle is listed starting from card 1 (rotations are the same arrangement)
    % Places[K] is the place of the K-th card the frog lands on, K = 0 to n-1; it starts on card 1, at place 0
    length(Places, N),
    Places ins 0..Last,
    Places = [0|_],
    % from a card k the frog jumps k places clockwise around the circle
    jumps(X, N, Places),
    % the frog jumps on every card: it lands on n different places
    all_distinct(Places),
    Vars = [X, Places].

% the card at place P (counting from 0) is C
card_at(X, P, C) :-
    I #= P + 1,
    element(I, X, C).

jumps(X, N, [P, Q|Rest]) :-
    !,
    card_at(X, P, Step),
    Q #= (P + Step) mod N,
    jumps(X, N, [Q|Rest]).
jumps(_, _, [_]).

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
