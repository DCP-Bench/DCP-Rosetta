% initials_queue: an ECLiPSe model from DCP Rosetta.
%
% The first 10 people in a queue for a Maths lecture each have initials which are an alphabetically
% ordered pair of distinct letters from the first five letters of the alphabet, A to E. No two people
% have the same initials, and no one shares a letter with the person in front of them. BE is at the
% front of the queue, CD is right behind, and BD is at the end. Work out the initials of the ten
% people, starting from the front.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).
:- lib(listut).

% The model reads no data fields. Letters are numbered 0 to 4 for A to E.
model(_Instance, Vars, [queue-Queue]) :-
    Size = 10,                             % people in the queue
    Last = 4,                              % the largest letter, E
    length(Queue, Size),
    % each person's initials are a pair [First, Second] of letters, First before Second
    ( foreach(Pair, Queue), param(Last) do
        Pair = [First, Second],
        First :: 0..Last,
        Second :: 0..Last,
        First #< Second
    ),
    % no two people have the same initials: the pairs are distinct
    ( foreach(Pair, Queue), foreach(Code, Codes), param(Last) do
        Pair = [First, Second],
        Code #= (Last + 1) * First + Second
    ),
    alldifferent(Codes),
    % BE is at the front of the queue, CD right behind it, and BD at the end
    nth1(1, Queue, [1, 4]),
    nth1(2, Queue, [2, 3]),
    nth1(Size, Queue, [1, 3]),
    % no one shares a letter with the person in front of them
    disjoint_from_front(Queue),
    flatten(Queue, Vars).

% each person's letters are different from both letters of the person in front
disjoint_from_front([_]).
disjoint_from_front([[A, B], [C, D] | Rest]) :-
    A #\= C,
    A #\= D,
    B #\= C,
    B #\= D,
    disjoint_from_front([[C, D] | Rest]).

:- lib(branch_and_bound).

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
