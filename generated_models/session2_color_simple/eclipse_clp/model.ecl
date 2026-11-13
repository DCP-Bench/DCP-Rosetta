% session2_color_simple: an ECLiPSe model from DCP Rosetta.
%
% We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands and
% Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to represent
% the colours. Find a colouring that minimizes the number of colours used.
%
% Save this file as model.ecl. Download `session2_color_simple.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session2_color_simple.json
%   eclipse -b model.ecl -e "run('session2_color_simple_1.dat'), halt"
%
% The data field: graph lists the neighbouring pairs of countries, each pair as two country numbers from 1 (the
% countries numbered in the order of the statement, Belgium first) that share a border.

:- lib(ic).
:- lib(listut).

% Output colors: the colour of each of the six countries, from 1 up.
model(Instance, [NumColors | Colors], [colors-Colors], min(NumColors)) :-
    memberchk(graph-Graph, Instance),
    NumCountries = 6,
    length(Colors, NumCountries),
    Colors :: 1..NumCountries,

    % NumColors is at least every colour given; minimised, it is the largest colour used, the number of colours used
    NumColors :: 1..NumCountries,
    ( foreach(Color, Colors), param(NumColors) do
        Color #=< NumColors
    ),

    % two neighbouring countries have different colours
    ( foreach(Edge, Graph), param(Colors) do
        Edge = [A, B],
        nth1(A, Colors, ColorA),
        nth1(B, Colors, ColorB),
        ColorA #\= ColorB
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
