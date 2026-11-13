% crypta: an ECLiPSe model from DCP Rosetta.
%
% Solve the cryptarithmetic puzzle: the 20-digit number BAIJJAJIIAHFCFEBBJEA plus the 20-digit
% number DHFGABCDIDBIFFAGFEJE equals the 20-digit number GJEGACDDHFAFJBFIHEEF, where every
% letter stands for a digit from 0 to 9, all letters stand for distinct digits, and the first
% letter of each number is not zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).
:- lib(listut).

model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E,
                        'F'-F, 'G'-G, 'H'-H, 'I'-I, 'J'-J]) :-
    % the letters, each a digit from 0 to 9
    Digits = [A, B, C, D, E, F, G, H, I, J],
    Digits :: 0..9,
    % all letters are distinct digits
    alldifferent(Digits),
    % the first letter of each number is not zero
    B #\= 0,
    D #\= 0,
    G #\= 0,
    % the three numbers, most significant digit first
    Summand1 = [B, A, I, J, J, A, J, I, I, A, H, F, C, F, E, B, B, J, E, A],
    Summand2 = [D, H, F, G, A, B, C, D, I, D, B, I, F, F, A, G, F, E, J, E],
    Total    = [G, J, E, G, A, C, D, D, H, F, A, F, J, B, F, I, H, E, E, F],
    % the carry out of each column, from the left: the leftmost column and the
    % rightmost column have no carry in or out, the others are 0 or 1
    length(Middle, 19),
    Middle :: 0..1,
    append([0 | Middle], [0], Carry),
    % column by column, the two summands and the carry from the right add up to the
    % digit of the total plus ten times the carry to the left
    ( for(P, 1, 20), param(Summand1, Summand2, Total, Carry) do
        nth1(P, Summand1, X),
        nth1(P, Summand2, Y),
        nth1(P, Total, Z),
        P1 is P + 1,
        nth1(P1, Carry, CarryIn),
        nth1(P, Carry, CarryOut),
        X + Y + CarryIn #= Z + 10 * CarryOut
    ),
    append(Digits, Middle, Vars).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

% Solves the model with no data (the empty list) and prints each output.
run :-
    solve_model([]).

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
