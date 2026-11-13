% flip_rows_cols: an ECLiPSe model from DCP Rosetta.
%
% Given is an array of positive and negative numbers. You can flip the sign of entire rows and columns, as many of them
% as you like. The goal is to make each one of all the rows and columns sum to positive numbers (or zero), and then to
% find the solution (there are more than one) that has the smallest overall sum.
%
% Save this file as model.ecl. Download `flip_rows_cols.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py flip_rows_cols.json
%   eclipse -b model.ecl -e "run('flip_rows_cols_1.dat'), halt"
%
% The data fields: input_matrix is the array, one list per row.

:- lib(ic).
:- lib(listut).

% Bs[I] is 1 when row I is flipped and Bc[J] is 1 when column J is flipped; the sign of a row or column is 1 - 2*B.
model(Instance, Vars, [row_signs-Rs, col_signs-Cs], min(sum(Flat))) :-
    memberchk(input_matrix-Matrix, Instance),
    length(Matrix, NR),
    Matrix = [FirstRow | _],
    length(FirstRow, NC),

    % each row and each column is either flipped or not
    length(Bs, NR), Bs :: 0..1,
    length(Bc, NC), Bc :: 0..1,
    ( foreach(B, Bs), foreach(R, Rs) do R #= 1 - 2*B ),
    ( foreach(B, Bc), foreach(C, Cs) do C #= 1 - 2*B ),

    % the column flips are labelled first: once they are fixed, each row's flip is forced by its row sum
    append(Bc, Bs, Vars),

    % the cell in row I and column J of the flipped array is A * (1-2*Bi) * (1-2*Bj), where A is the input value; with
    % P = Bi * Bj as a 0/1 variable this is linear: A - 2A*Bi - 2A*Bj + 4A*P
    ( foreach(Row, Matrix), foreach(XRow, Xss), foreach(Bi, Bs), param(Bc) do
        ( foreach(A, Row), foreach(Bj, Bc), foreach(X, XRow), param(Bi) do
            P #:: 0..1,
            P #=< Bi,
            P #=< Bj,
            P #>= Bi + Bj - 1,
            X #= A - 2*A*Bi - 2*A*Bj + 4*A*P
        )
    ),
    flatten(Xss, Flat),

    % each row of the flipped array sums to a positive number or zero
    ( foreach(XRow, Xss) do
        sum(XRow) #>= 0
    ),

    % each column of the flipped array sums to a positive number or zero
    ( for(J, 1, NC), param(Xss) do
        ( foreach(XRow, Xss), foreach(X, Col), param(J) do
            nth1(J, XRow, X)
        ),
        sum(Col) #>= 0
    ).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

:- lib(branch_and_bound).

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
