% isbn: an ECLiPSe model from DCP Rosetta.
%
% An ISBN-13 is a 13-digit number whose last digit is a check digit. Multiply the first 12 digits
% alternately by 1 and 3, starting with 1, and sum the products; the check digit is (10 - sum mod 10)
% mod 10, which makes the sum with the check digit a multiple of 10. An ISBN-13 starts with 978 or
% 979. Some digits are unknown, and the model finds values for them that make a valid ISBN-13.
%
% Save this file as model.ecl. Download `isbn.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py isbn.json
%   eclipse -b model.ecl -e "run('isbn_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field isbn_init holds the 13 digits, with -1 for each unknown digit.
model(Data, Vars, [isbn-Isbn]) :-
    memberchk(isbn_init-Init, Data),
    length(Isbn, 13),
    % each digit is 0 to 9, and a known digit keeps its value
    ( foreach(X, Isbn), foreach(G, Init) do
        X :: 0..9,
        ( G =:= -1 -> true ; X = G )
    ),
    % the number starts with 978 or 979
    Isbn = [D1, D2, D3 | _],
    D1 #= 9,
    D2 #= 7,
    D3 :: 8..9,
    % the first twelve digits, multiplied alternately by 1 and 3 starting with 1, give the weighted sum
    ( for(I, 1, 12), foreach(W, Weighted), param(Isbn) do
        nth1(I, Isbn, X),
        Odd is I mod 2,
        ( Odd =:= 1 -> W #= X ; W #= 3 * X )
    ),
    sum(Weighted) #= Sum,
    % the last digit is the check digit: the weighted sum plus the check digit is a multiple of 10
    nth1(13, Isbn, Check),
    Sum + Check #= 10 * Q,
    % Q is the multiple of 10 reached by the weighted sum plus the check digit, divided by 10 (at most 22, so 0..50 is ample)
    Q :: 0..50,
    Vars = [Q | Isbn].

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
