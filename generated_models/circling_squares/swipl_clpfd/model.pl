% circling_squares: a SWI-Prolog model from DCP Rosetta.
%
% Place a different whole number in each of ten squares arranged in a circle, so that for any two adjacent numbers
% the sum of their squares equals the sum of the squares of the two numbers diametrically opposite to them. The
% numbers are positive whole numbers of at most two figures. The ten squares are lettered A, B, C, D, E, F, G, H, I, K
% in circle order, and A=16, B=2, F=8 and G=14.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I, 'K'-K]) :-
    Vars = [A, B, C, D, E, F, G, H, I, K],  % the squares in circle order
    Vars ins 1..99,                         % positive whole numbers of at most two figures (the puzzle: no number need have more)
    all_distinct(Vars),
    % the four numbers given in the problem
    A #= 16, B #= 2, F #= 8, G #= 14,
    % the sums of squares of two adjacent numbers and of the two opposite them are equal
    balanced(A, B, F, G),
    balanced(B, C, G, H),
    balanced(C, D, H, I),
    balanced(D, E, I, K),
    balanced(E, F, K, A).

% the squares of P and Q sum to the squares of R and S
balanced(P, Q, R, S) :-
    P * P + Q * Q #= R * R + S * S.

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
