% csplib_009_perfect_square_placement: an ECLiPSe model from DCP Rosetta.
%
% Perfect square placement (the squared square problem): pack a set of squares with given integer
% sides into a bigger square of a given base, such that no squares overlap each other and all
% square borders are parallel to the border of the big square. The sum of the square surfaces is
% equal to the surface of the packing square, so there is no spare capacity.
%
% Save this file as model.ecl. Download `csplib_009_perfect_square_placement.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_009_perfect_square_placement.json
%   eclipse -b model.ecl -e "run('csplib_009_perfect_square_placement_1.dat'), halt"

% Fields read from the data: base (the side of the big square) and sides (the side of each
% square, indexed from 0; the number of squares is the length of sides).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['x_coords'-Xs, 'y_coords'-Ys]) :-
    memberchk(base-Base, Instance),
    memberchk(sides-Sides, Instance),
    length(Sides, NumSquares),
    length(Xs, NumSquares),
    length(Ys, NumSquares),
    % each square lies inside the big square, so its corner is between 0 and base minus its side
    ( for(I, 1, NumSquares), param(Xs, Ys, Sides, Base) do
        nth1(I, Sides, S),
        Limit is Base - S,
        nth1(I, Xs, X),
        nth1(I, Ys, Y),
        X :: 0..Limit,
        Y :: 0..Limit
    ),
    % no two squares overlap: for each pair, one lies to the left of the other, or one lies
    % below the other
    ( for(Row, 1, NumSquares), param(Xs, Ys, Sides, NumSquares) do
        Row1 is Row + 1,
        nth1(Row, Xs, XI), nth1(Row, Ys, YI), nth1(Row, Sides, SI),
        ( for(Col, Row1, NumSquares), param(Xs, Ys, Sides, XI, YI, SI) do
            nth1(Col, Xs, XJ), nth1(Col, Ys, YJ), nth1(Col, Sides, SJ),
            Left1 #= (XI + SI #=< XJ),
            Left2 #= (XJ + SJ #=< XI),
            Below1 #= (YI + SI #=< YJ),
            Below2 #= (YJ + SJ #=< YI),
            Left1 + Left2 + Below1 + Below2 #>= 1
        )
    ),
    flatten([Xs, Ys], Vars).

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
