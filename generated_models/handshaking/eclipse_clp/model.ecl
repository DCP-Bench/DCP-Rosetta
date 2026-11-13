% handshaking: an ECLiPSe model from DCP Rosetta.
%
% Hilary and Jocelyn are married. They invite a number of couples who are friends. After some handshaking, in which nobody shakes hands with
% themselves or with their spouse,
% Jocelyn then asks how many hands each person has shaken, and all the answers are different.
% The model finds the number of hands Hilary has shaken.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
% Save this file as model.ecl. Download `handshaking.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py handshaking.json
%   eclipse -b model.ecl -e "run('handshaking_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field num_couples is the number of couples invited besides Hilary and Jocelyn.
% People are numbered from 1: 1 is Hilary, 2 is Jocelyn, and each invited couple takes the next two numbers.
model(Data, Vars, [hil-Hil]) :-
    memberchk(num_couples-C, Data),
    M is C + 1,                            % couples in all, Hilary and Jocelyn's included
    N is 2 * M,                            % people in all
    Max is N - 2,                          % a person can shake hands with everyone except self and spouse
    % Rows[I][J] is 1 when person I shakes hands with person J
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        ( foreach(V, Row) do V :: 0..1 )
    ),
    % nobody shakes hands with him or herself
    ( for(I, 1, N), param(Rows) do cell(Rows, I, I, 0) ),
    % nobody shakes hands with his or her spouse: the couples are the pairs (1,2), (3,4), ...
    ( for(K, 1, M), param(Rows) do
        I1 is 2 * K - 1,
        I2 is 2 * K,
        cell(Rows, I1, I2, 0)
    ),
    % a handshake is the same from both sides
    ( for(I, 1, N), param(Rows, N) do
        ( for(J, I + 1, N), param(Rows, I) do
            cell(Rows, I, J, V),
            cell(Rows, J, I, V)
        )
    ),
    % the number of hands each person has shaken is the sum of his or her row
    length(Ds, N),
    ( foreach(Row, Rows), foreach(D, Ds), param(Max) do
        sum(Row) #= D,
        D :: 0..Max
    ),
    % all the answers are different: Jocelyn's count is not one of the answers she asks for
    Ds = [Hil, _Jocelyn | Others],
    alldifferent([Hil | Others]),
    flatten(Rows, Hands),
    append(Hands, Ds, Vars).

% cell(Rows, I, J, V): V is the entry in row I, column J
cell(Rows, I, J, V) :-
    nth1(I, Rows, Row),
    nth1(J, Row, V).

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
