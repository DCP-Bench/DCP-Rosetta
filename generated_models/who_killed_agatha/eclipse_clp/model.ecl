% who_killed_agatha: an ECLiPSe model from DCP Rosetta.
%
% Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and Charles live in Dreadsbury Mansion, and are
% the only ones to live there. A killer always hates, and is no richer than his victim. Charles hates no one that
% Agatha hates. Agatha hates everybody except the butler. The butler hates everyone not richer than Aunt Agatha. The
% butler hates everyone whom Agatha hates. No one hates everyone. Who killed Agatha?
%
% Save this file as model.ecl. Download `who_killed_agatha.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py who_killed_agatha.json
%   eclipse -b model.ecl -e "run('who_killed_agatha_1.dat'), halt"

% Data fields: names (the names of the three people, a list indexed from 0: Agatha, the butler, Charles).
% Output killer: the 0-based index of the killer.
% Persons are numbered from 1 inside the model: Agatha, the butler and Charles are at the positions of the names.
% Hates[X,Y] is 1 when person X hates person Y. Wealth[X] is the rank of person X's wealth: X is richer than Y
% when Wealth[X] > Wealth[Y].
:- lib(ic).

model(Instance, Vars, [killer-Killer]) :-
    memberchk(names-Names, Instance),
    index_of("Agatha herself", Names, Agatha),       % 0-based positions in the names
    index_of("the butler", Names, Butler),
    index_of("Charles", Names, Charles),
    length(Names, N),                                 % the number of people
    NN1 is N - 1,
    dim(Hates, [N, N]),
    Hates[1..N, 1..N] :: 0..1,
    dim(Wealth, [N]),
    Wealth[1..N] :: 0..NN1,
    % the killer is one of the people in the mansion
    Killer :: 0..NN1,
    % a killer always hates his victim, Agatha, and is no richer than she is
    AgathaP is Agatha + 1,
    ( for(P, 1, N), param(Killer, Hates, Wealth, AgathaP) do
        (   (Killer #= P - 1) =>
            (Hates[P, AgathaP] #= 1 and Wealth[P] #=< Wealth[AgathaP])
        )
    ),
    % the hatred requirements of the puzzle, for each person J in turn
    ButlerP is Butler + 1,
    CharlesP is Charles + 1,
    ( for(J, 1, N), param(Hates, Wealth, AgathaP, ButlerP, CharlesP) do
        % Agatha hates everybody except the butler
        (   J =:= ButlerP
        ->  Hates[AgathaP, J] #= 0
        ;   Hates[AgathaP, J] #= 1
        ),
        % Charles hates no one that Agatha hates
        ( (Hates[AgathaP, J] #= 1) => (Hates[CharlesP, J] #= 0) ),
        % the butler hates everyone not richer than Agatha
        ( (Wealth[J] #=< Wealth[AgathaP]) => (Hates[ButlerP, J] #= 1) ),
        % the butler hates everyone whom Agatha hates
        ( (Hates[AgathaP, J] #= 1) => (Hates[ButlerP, J] #= 1) )
    ),
    % no one hates everyone: each person hates fewer than N people
    ( for(I, 1, N), param(Hates, N) do
        collection_to_list(Hates[I, 1..N], Row),
        sum(Row) #< N
    ),
    flatten_array(Wealth, WealthList),
    flatten_array(Hates, HatesList),
    append([Killer | WealthList], HatesList, Vars).

% The index (from 0) of the first element of the list equal to the name.
index_of(Name, [Name|_], 0) :- !.
index_of(Name, [_|Rest], I) :-
    index_of(Name, Rest, J),
    I is J + 1.

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
