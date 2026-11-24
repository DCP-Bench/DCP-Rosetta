% cell_tower: an ECLiPSe model from DCP Rosetta.
%
% A telecom company builds cell towers at some of the potential sites to cover the inhabitants of a city. The city is
% split into regions, each with a known population, and a tower covers the regions it reaches. Only a limited budget is
% available, so the company chooses which sites to build on in order to cover as many people as possible.
%
% Save this file as model.ecl. Download `cell_tower.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py cell_tower.json
%   eclipse -b model.ecl -e "run('cell_tower_1.dat'), halt"
%
% Data fields: budget is the total budget for building towers; cost is the cost of building each tower site; delta is
% the coverage matrix, with entry [t][r] equal to 1 when a tower at site t covers region r; population is the population
% of each region (all lists indexed from 0 as in the JSON).
:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Outputs: build_tower (whether a tower is built at each site) and total_population_covered (the population covered).
model(Instance, Vars, [build_tower-Ts, total_population_covered-Total], max(Total)) :-
    memberchk(budget-Budget, Instance),
    memberchk(cost-Cost, Instance),
    memberchk(delta-Delta, Instance),
    memberchk(population-Population, Instance),
    length(Cost, NT),
    length(Population, NR),
    length(Ts, NT),
    Ts :: 0..1,
    length(Cs, NR),
    Cs :: 0..1,
    % the towers built cost no more than the budget
    Spent #= Cost * Ts,
    Spent #=< Budget,
    % a region counts as covered only when a tower built at a site that reaches it
    columns_of(Delta, Cols),
    covered_by(Cs, Cols, Ts),
    % the population covered is the population of the covered regions, to be maximized
    Total #= Population * Cs,
    append(Ts, Cs, Vars1),
    append(Vars1, [Spent, Total], Vars).

% covered_by(Cs, Cols, Ts): region r is covered (Cs entry 1) only if some tower built covers it
covered_by([], [], _).
covered_by([C | Cs], [Col | Cols], Ts) :-
    Hit #= Col * Ts,
    C #=< Hit,
    covered_by(Cs, Cols, Ts).

% columns_of(Rows, Cols): Cols is the transpose of the matrix Rows
columns_of([[] | _], []) :- !.
columns_of(Rows, [Col | Cols]) :-
    firsts_rests(Rows, Col, Rest),
    columns_of(Rest, Cols).

firsts_rests([], [], []).
firsts_rests([[H | T] | Rs], [H | Hs], [T | Ts]) :-
    firsts_rests(Rs, Hs, Ts).

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
