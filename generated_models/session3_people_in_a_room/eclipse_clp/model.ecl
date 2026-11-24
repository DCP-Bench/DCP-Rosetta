% session3_people_in_a_room: an ECLiPSe model from DCP Rosetta.
%
% There are 13 people, 4 of them male. They enter a room one at a time, in an order to be chosen. Find an order
% in which the males and females enter so that, at any time, the ratio of females to males in the room is no
% greater than 7/3.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data: the number of people and of males are named in the model.

:- lib(ic).
:- lib(lists).

% Seq: the people in order of entry, 0 for a male and 1 for a female.
model(_Instance, Seq, [sequence-Seq]) :-
    NumPeople = 13,
    NumMales = 4,
    length(Seq, NumPeople),
    Seq :: 0..1,
    % the rest of the people are female
    sum(Seq) #= NumPeople - NumMales,
    % after each entry, the females F and males M in the room satisfy F / M <= 7 / 3, i.e. 3 F <= 7 M
    ( for(K, 1, NumPeople), param(Seq) do
        length(Head, K),
        append(Head, _, Seq),
        3 * sum(Head) #=< 7 * (K - sum(Head))
    ).

:- lib(branch_and_bound).

% Solves the model and prints each output.
run :- solve_model([]).

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
