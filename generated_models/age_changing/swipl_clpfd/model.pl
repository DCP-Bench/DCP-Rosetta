% age_changing: a SWI-Prolog model from DCP Rosetta.
%
% If you start with my age, in years, and apply the four operations +2, /8, -3 and *7 in some order, then the final
% answer you get is my husband's age.
%
% Funnily enough, if you start with his age and apply the same four operations in a different order, then you get my
% age.
%
% Both ages are between 16 and 120, and every intermediate result is a positive integer, so a division by 8 must be
% exact.
%
% What are our two ages?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

% my age is M and my husband's age is H; each order is a list of operation codes (1: +2, 2: /8, 3: -3, 4: *7)
model(_Instance, Vars, [m-M, h-H]) :-
    [M, H] ins 16..120,
    Ops1 = [P1, P2, P3, P4], Ops1 ins 1..4, all_distinct(Ops1),
    Ops2 = [Q1, Q2, Q3, Q4], Ops2 ins 1..4, all_distinct(Ops2),
    % my age, through the four operations in the first order, gives my husband's age
    chain(Ops1, M, Mids1, H),
    % his age, through the four operations in the second order, gives my age
    chain(Ops2, H, Mids2, M),
    % the second order is a different order from the first
    (P1 #\= Q1) #\/ (P2 #\= Q2) #\/ (P3 #\= Q3) #\/ (P4 #\= Q4),
    append([[M, H], Ops1, Ops2, Mids1, Mids2], Vars).

% applying the operations Ops in order to Start gives End, with the intermediate results Mids
chain([Op1, Op2, Op3, Op4], Start, [A, B, C], End) :-
    step(Op1, Start, A),
    step(Op2, A, B),
    step(Op3, B, C),
    step(Op4, C, End).

% Y is X after the operation Op; every intermediate result is a positive integer, and a division must be exact
step(Op, X, Y) :-
    [X, Y] ins 1..1000,
    % +2
    (Op #= 1) #==> (Y #= X + 2),
    % /8, exact
    (Op #= 2) #==> (X #= 8 * Y),
    % -3
    (Op #= 3) #==> (Y #= X - 3),
    % *7
    (Op #= 4) #==> (Y #= 7 * X).

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
