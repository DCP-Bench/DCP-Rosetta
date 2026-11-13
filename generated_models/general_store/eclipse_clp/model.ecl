% general_store: an ECLiPSe model from DCP Rosetta.
%
% The owner of a general store, who is something of a puzzlist, has put up a sign to see if any of his mathematical
% friends can translate it properly. Each different letter stands for a different digit. The words CHESS, CASH, BOWWOW,
% CHOPS, ALSOPS, PALEALE, COOL, BASS, HOPS, ALES, HOES, APPLES, COWS, CHEESE, CHSOAP and SHEEP add up to ALLWOOL.
% Leading zeros are allowed: a word may start with the digit 0.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% The variables are the digits of the letters C, H, E, S, A, B, O, W, P, L; each word is read as the number its digits
% spell.
model(_Instance, Vars, Outputs) :-
    Vars = [C, H, E, S, A, B, O, W, P, L],
    Vars :: 0..9,

    % each different letter stands for a different digit
    alldifferent(Vars),

    % the numbers spelled by the words above the line
    NChess   :: 0..99999,
    NCash    :: 0..9999,
    NBowwow  :: 0..999999,
    NChops   :: 0..99999,
    NAlsops  :: 0..999999,
    NPaleale :: 0..9999999,
    NCool    :: 0..9999,
    NBass    :: 0..9999,
    NHops    :: 0..9999,
    NAles    :: 0..9999,
    NHoes    :: 0..9999,
    NApples  :: 0..999999,
    NCows    :: 0..9999,
    NCheese  :: 0..999999,
    NChsoap  :: 0..999999,
    NSheep   :: 0..99999,
    NAllwool :: 0..9999999,
    NChess   #= 10000*C + 1000*H + 100*E + 10*S + S,
    NCash    #= 1000*C + 100*A + 10*S + H,
    NBowwow  #= 100000*B + 10000*O + 1000*W + 100*W + 10*O + W,
    NChops   #= 10000*C + 1000*H + 100*O + 10*P + S,
    NAlsops  #= 100000*A + 10000*L + 1000*S + 100*O + 10*P + S,
    NPaleale #= 1000000*P + 100000*A + 10000*L + 1000*E + 100*A + 10*L + E,
    NCool    #= 1000*C + 100*O + 10*O + L,
    NBass    #= 1000*B + 100*A + 10*S + S,
    NHops    #= 1000*H + 100*O + 10*P + S,
    NAles    #= 1000*A + 100*L + 10*E + S,
    NHoes    #= 1000*H + 100*O + 10*E + S,
    NApples  #= 100000*A + 10000*P + 1000*P + 100*L + 10*E + S,
    NCows    #= 1000*C + 100*O + 10*W + S,
    NCheese  #= 100000*C + 10000*H + 1000*E + 100*E + 10*S + E,
    NChsoap  #= 100000*C + 10000*H + 1000*S + 100*O + 10*A + P,
    NSheep   #= 10000*S + 1000*H + 100*E + 10*E + P,
    NAllwool #= 1000000*A + 100000*L + 10000*L + 1000*W + 100*O + 10*O + L,

    % the words above the line add up to ALL WOOL
    NChess + NCash + NBowwow + NChops + NAlsops + NPaleale + NCool + NBass
        + NHops + NAles + NHoes + NApples + NCows + NCheese + NChsoap + NSheep
        #= NAllwool,

    Outputs = ['A'-A, 'B'-B, 'C'-C, 'E'-E, 'H'-H, 'L'-L, 'O'-O, 'P'-P, 'S'-S, 'W'-W].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Builds the model, solves it and prints each output.
run :- solve_model([]).

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
