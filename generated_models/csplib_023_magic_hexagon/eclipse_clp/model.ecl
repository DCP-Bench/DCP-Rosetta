% csplib_023_magic_hexagon: an ECLiPSe model from DCP Rosetta.
%
% Arrange the numbers 1 to 19 in a hexagon, with cells A to S in rows of 3, 4, 5, 4 and 3 cells:
%
%       A, B, C
%      D, E, F, G
%     H, I, J, K, L
%      M, N, O, P
%       Q, R, S
%
% so that the sum of the numbers in each of the 15 lines (rows and diagonals) equals the magic constant, 38.
%
% Save this file as model.ecl. Download `csplib_023_magic_hexagon.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_023_magic_hexagon.json
%   eclipse -b model.ecl -e "run('csplib_023_magic_hexagon_1.dat'), halt"

% Instance fields: NUM_CELLS (the number of cells, 19, which are numbered 1 to NUM_CELLS) and MAGIC_SUM (the magic
% constant, the sum of each line). Output LD: the values of A, B, ..., S in that order.

:- lib(ic).

model(Instance, Vars, ['LD'-Vars]) :-
    memberchk('NUM_CELLS'-Cells, Instance),
    memberchk('MAGIC_SUM'-Magic, Instance),
    Vars = [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S],
    length(Vars, Cells),
    % each cell holds a number from 1 to the number of cells
    Vars :: 1..Cells,

    % all the numbers of the hexagon are different
    alldifferent(Vars),

    % the sum of the numbers in each of the 5 horizontal rows is the magic constant
    A + B + C #= Magic,
    D + E + F + G #= Magic,
    H + I + J + K + L #= Magic,
    M + N + O + P #= Magic,
    Q + R + S #= Magic,

    % the sum of the numbers in each of the 5 diagonals from upper left to lower right is the magic constant
    A + E + J + O + S #= Magic,
    B + F + K + P #= Magic,
    C + G + L #= Magic,
    D + I + N + R #= Magic,
    H + M + Q #= Magic,

    % the sum of the numbers in each of the 5 diagonals from upper right to lower left is the magic constant
    C + F + J + N + Q #= Magic,
    B + E + I + M #= Magic,
    A + D + H #= Magic,
    G + K + O + R #= Magic,
    L + P + S #= Magic.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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
