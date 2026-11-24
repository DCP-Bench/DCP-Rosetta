% bales_of_hay: an ECLiPSe model from DCP Rosetta.
%
% You have a number of bales of hay. They were weighed in all possible combinations of two, and the weights of
% these combinations were written down and arranged in numerical order, without keeping track of which weight matched
% which pair of bales. Find the weight of each bale.
%
% Save this file as model.ecl. Download `bales_of_hay.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py bales_of_hay.json
%   eclipse -b model.ecl -e "run('bales_of_hay_1.dat'), halt"

% Fields read: n is the number of bales, weights is the list of the pair weights in numerical order, indexed from 0.

:- lib(ic).
:- lib(listut).

% Output bales: the weight of each bale, in the order of the bales.
model(Instance, Bales, [bales-Bales]) :-
    memberchk(n-N, Instance),
    memberchk(weights-Weights, Instance),
    length(Weights, NumPairs),
    % there is one weight for each pair of bales
    NumPairs =:= N * (N - 1) // 2,
    % the heaviest pair weight bounds the weight of every bale
    ( foreach(W, Weights), fromto(0, A, B, Max) do B is max(A, W) ),
    length(Bales, N),
    Bales :: 0..Max,

    % each pair of bales I < J is weighed once: its weight is the sum of the two bales
    all_pairs(N, Pairs),
    % the weights are matched to the pairs one to one: each pair takes a different weight of the list
    length(Index, NumPairs),
    Index :: 1..NumPairs,
    alldifferent(Index),
    post_pairs(Pairs, Index, Bales, Weights).

% the pairs I-J with 1 =< I < J =< N, in order
all_pairs(N, Pairs) :- all_pairs(1, N, Pairs, []).

all_pairs(I, N, Pairs, Tail) :- I >= N, !, Pairs = Tail.
all_pairs(I, N, Pairs, Tail) :-
    J0 is I + 1,
    pair_row(I, J0, N, Pairs, Mid),
    I1 is I + 1,
    all_pairs(I1, N, Mid, Tail).

pair_row(_, J, N, Pairs, Tail) :- J > N, !, Pairs = Tail.
pair_row(I, J, N, [I-J | Pairs], Tail) :-
    J1 is J + 1,
    pair_row(I, J1, N, Pairs, Tail).

% the weight of the pair I-J, taken from the list at the position chosen for it, is the sum of the two bales
post_pairs([], [], _, _).
post_pairs([I-J | Pairs], [X | Xs], Bales, Weights) :-
    nth1(I, Bales, BI),
    nth1(J, Bales, BJ),
    Sum #= BI + BJ,
    element(X, Weights, Sum),
    post_pairs(Pairs, Xs, Bales, Weights).

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
