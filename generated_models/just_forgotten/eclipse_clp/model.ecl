% just_forgotten: an ECLiPSe model from DCP Rosetta.
%
% Joe's bank account number has all the digits from 0 to n-1 in some order. He tried several sets of
% digits, each a guess at the number, and in each set just a specific number of the digits were in their
% correct position. Knowing that number for each set is enough to work out the account number. Find it.
%
% Save this file as model.ecl. Download `just_forgotten.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py just_forgotten.json
%   eclipse -b model.ecl -e "run('just_forgotten_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field sets holds the guesses, each a list of n digits. The data field num_correct_digits is
% the number of digits in the correct position in each set.
model(Data, Vars, [x-X]) :-
    memberchk(sets-Sets, Data),
    memberchk(num_correct_digits-K, Data),
    Sets = [FirstSet | _],
    length(FirstSet, N),
    length(X, N),
    % the account number has the digits from 0 to n-1, each once
    X :: 0..N-1,
    alldifferent(X),
    % each guess has exactly K digits in the same position as the account number
    ( foreach(Set, Sets), param(X, K) do
        same_position(X, Set, Matches),
        sum(Matches) #= K
    ),
    Vars = X.

% same_position(Xs, Set, Matches): Matches[J] is 1 when the digit at position J of Set is Xs[J]
same_position(Xs, Set, Matches) :-
    ( foreach(X, Xs), foreach(D, Set), foreach(M, Matches) do
        (X #= D) <=> (M #= 1),
        M :: 0..1
    ).

:- lib(branch_and_bound).

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
