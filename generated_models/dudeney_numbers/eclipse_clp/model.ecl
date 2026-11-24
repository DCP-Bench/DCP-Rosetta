% dudeney_numbers: an ECLiPSe model from DCP Rosetta.
%
% A Dudeney number is a positive integer that is a perfect cube such that the sum of its digits is equal to the
% cube root of the number. Find a Dudeney number that is larger than 1 and has at most n digits.
%
% Save this file as model.ecl. Download `dudeney_numbers.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py dudeney_numbers.json
%   eclipse -b model.ecl -e "run('dudeney_numbers_1.dat'), halt"

% Data fields: n (the largest number of digits the Dudeney number may have).

:- lib(ic).
:- lib(lists).

model(Instance, [Root | Digits], [number-Number]) :-
    memberchk(n-N, Instance),
    length(Digits, N),
    Digits :: 0..9,
    % the number has at most n digits, so it is at most 10^n - 1
    Largest is 10 ^ N - 1,
    cube_root_floor(Largest, MaxRoot),
    % the number is the cube of Root, and it is larger than 1, so Root is at least 2
    Root :: 2..MaxRoot,
    Number #= Root * Root * Root,
    % the number written as its n digits, the lowest digit first
    (   for(I, 0, N - 1), foreach(D, Digits), foreach(T, Terms) do
        Weight is 10 ^ I,
        T #= Weight * D
    ),
    Number #= sum(Terms),
    % the sum of the digits of the number is equal to the cube root of the number
    sum(Digits) #= Root.

% cube_root_floor(+Bound, -Root): Root is the largest integer whose cube is at most Bound.
cube_root_floor(Bound, Root) :-
    cube_root_floor(1, Bound, Root).

cube_root_floor(R, Bound, Root) :-
    (   (R + 1) ^ 3 =< Bound
    ->  R1 is R + 1, cube_root_floor(R1, Bound, Root)
    ;   Root = R
    ).

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
