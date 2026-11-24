% kakuro: an ECLiPSe model from DCP Rosetta.
%
% A Kakuro puzzle is a grid of white and black cells. Insert a digit from 1 to 9 into each white cell so
% that the digits in each entry (a run of white cells across or down, with its clue) add up to the clue,
% and no digit is repeated in an entry. Black cells hold 0.
%
% Save this file as model.ecl. Download `kakuro.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py kakuro.json
%   eclipse -b model.ecl -e "run('kakuro_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field n is the size of the grid, n rows by n columns. The data field blanks lists the black
% cells as [Row, Column], counted from 1; every other cell is white. The data field problem lists the
% entries, each as [Clue, Cell, Cell, ...] with the cells as [Row, Column].
model(Data, Vars, [x-Grid]) :-
    memberchk(n-N, Data),
    memberchk(blanks-Blanks, Data),
    memberchk(problem-Entries, Data),
    length(Grid, N),
    ( foreach(Row, Grid), param(N) do length(Row, N) ),
    % each white cell holds a digit from 1 to 9, each black cell holds 0
    ( for(R, 1, N), param(Grid, N, Blanks) do
        nth1(R, Grid, Row),
        ( for(C, 1, N), param(Row, R, Blanks) do
            nth1(C, Row, X),
            (   memberchk([R, C], Blanks) -> X = 0 ; X :: 1..9 )
        )
    ),
    % each entry has distinct digits that add up to its clue
    ( foreach(Entry, Entries), param(Grid) do
        Entry = [Clue | Cells],
        entry_values(Cells, Grid, Values),
        alldifferent(Values),
        sum(Values) #= Clue
    ),
    flatten(Grid, Vars).

% entry_values(Cells, Grid, Values): Values holds the digits in the given cells of the grid
entry_values([], _, []).
entry_values([[R, C] | Cells], Grid, [V | Values]) :-
    nth1(R, Grid, Row),
    nth1(C, Row, V),
    entry_values(Cells, Grid, Values).

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
