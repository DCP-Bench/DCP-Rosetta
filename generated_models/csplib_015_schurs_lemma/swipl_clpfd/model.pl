% csplib_015_schurs_lemma: a SWI-Prolog model from DCP Rosetta.
%
% Put the balls labelled 1 to n into c boxes so that for every triple of balls (x, y, z) with x + y = z (x and y may be
% equal), not all three are in the same box. The statement has 3 boxes (c = 3), for which a solution exists only when n is less than 14.
%
% Save this file as model.pl. Download `csplib_015_schurs_lemma.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_015_schurs_lemma.json')" -t halt model.pl
%
% Data fields: n (the number of balls, labelled 1 to n) and c (the number of boxes).
:- use_module(library(clpfd)).

model(Instance, Vars, [balls-Balls]) :-
    N = Instance.n,
    Boxes = Instance.c,
    % Balls[I] is the box, from 1 to c, that ball I is in
    length(Balls, N),
    Balls ins 1..Boxes,
    Vars = Balls,
    % for every x, y with x + y = z <= n, the three balls x, y and z are not all in the same box
    findall(X-Y, (between(1, N, X), between(X, N, Y), X + Y =< N), Triples),
    maplist(not_same_box(Balls), Triples).

% the balls X, Y and X + Y are not all in one box
not_same_box(Balls, X-Y) :-
    Z is X + Y,
    nth1(X, Balls, BX),
    nth1(Y, Balls, BY),
    nth1(Z, Balls, BZ),
    #\ (BX #= BY #/\ BY #= BZ).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
