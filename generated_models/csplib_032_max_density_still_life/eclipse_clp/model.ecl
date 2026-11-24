% csplib_032_max_density_still_life: an ECLiPSe model from DCP Rosetta.
%
% Find the most densely populated stable pattern (a still life) of Conway's Game of Life on an n by m active grid. A
% still life does not change from one generation to the next: a live cell has exactly 2 or 3 live neighbours, and a dead
% cell, including a dead cell just outside the active grid, does not have exactly 3 live neighbours. Cells outside the
% grid are dead. Maximise the number of live cells in the grid.
%
% Save this file as model.ecl. Download `csplib_032_max_density_still_life.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_032_max_density_still_life.json
%   eclipse -b model.ecl -e "run('csplib_032_max_density_still_life_1.dat'), halt"
%
% The instance fields: n (rows of the active grid), m (columns of the active grid).

:- lib(ic).
:- lib(branch_and_bound).
:- lib(listut).

% Output grid: the n by m active grid, Grid[I][J] is 1 when the cell in row I and column J is alive, counting from 1.
model(Instance, Vars, [grid-Inner], max(sum(Vars))) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    N2 is N + 2,                           % the active grid with a ring of dead cells around it
    M2 is M + 2,
    length(Inner, N),
    ( foreach(Row, Inner), param(M) do length(Row, M) ),
    flatten(Inner, Vars),
    Vars :: 0..1,
    % the ring of dead cells around the grid, padding the active grid with 0s
    length(Zeros, M2),
    ( foreach(Z, Zeros) do Z = 0 ),
    ( foreach(Row, Inner), foreach(Padded, PaddedRows) do append([0|Row], [0], Padded) ),
    Grid = [Zeros|Rest],
    append(PaddedRows, [Zeros], Rest),

    % every cell of the padded grid obeys the rules of a still life
    ( for(I, 1, N2), param(Grid, N2, M2) do
        ( for(J, 1, M2), param(Grid, I, N2, M2) do
            nth1(I, Grid, RowI),
            nth1(J, RowI, X),
            % the live neighbours of the cell (the 8 cells around it, outside cells are dead)
            ( foreach([DI, DJ], [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]),
              foreach(C, Neighbours), param(Grid, I, J, N2, M2) do
                I2 is I + DI, J2 is J + DJ,
                (   I2 >= 1, I2 =< N2, J2 >= 1, J2 =< M2
                ->  nth1(I2, Grid, RowN), nth1(J2, RowN, C)
                ;   C = 0
                )
            ),
            Ns #= sum(Neighbours),
            (   I >= 2, I =< N2 - 1, J >= 2, J =< M2 - 1
            ->  % a live cell has 2 or 3 live neighbours
                Few #= (Ns #< 2),
                Many #= (Ns #> 3),
                Few + X #=< 1,
                Many + X #=< 1,
                % a dead cell does not have exactly 3 live neighbours
                Three #= (Ns #= 3),
                Three #=< X
            ;   % a dead cell outside the grid does not have exactly 3 live neighbours
                Ns #\= 3
            )
        )
    ).

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
