% csplib_018_water_bucket: an ECLiPSe model from DCP Rosetta.
%
% You are given an 8 pint bucket of water, and two empty buckets which can contain 5 and 3 pints respectively. The water
% is to be divided into two: 4 pints must end up in the 8 pint bucket and 4 pints in the 5 pint bucket. A transfer pours
% water from one bucket into another until the first is empty or the second is full. Find the minimum number of
% transfers of water between buckets that reaches the goal.
%
% Save this file as model.ecl. Download `csplib_018_water_bucket.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_018_water_bucket.json
%   eclipse -b model.ecl -e "run('csplib_018_water_bucket_1.dat'), halt"

% Instance fields: capacities (the capacity of each bucket), initial_state and goal_state (the water in each bucket),
% MAX_STEPS (the length of the output sequence) and PADDING_VALUE (the value written after the goal state). Buckets are
% indexed from 0 as in the JSON.
% Outputs: cost, the number of transfers, and sequence, the states from the initial state to the goal, one list of
% bucket contents per row, padded with PADDING_VALUE after the goal state.

:- lib(ic).
:- lib(lists).

model(Instance, Vars, Outputs, min(Cost)) :-
    memberchk(capacities-Caps, Instance),
    memberchk(initial_state-Init, Instance),
    memberchk(goal_state-Goal, Instance),
    memberchk('MAX_STEPS'-Max, Instance),
    memberchk('PADDING_VALUE'-Pad, Instance),
    % States[I] is the water in the three buckets after I transfers
    length(States, Max),
    % each bucket holds between 0 and its capacity pints
    ( foreach(St, States), param(Caps) do
        St = [A,B,C], Caps = [Ca,Cb,Cc],
        A :: 0..Ca, B :: 0..Cb, C :: 0..Cc
    ),
    % the first state is the initial state
    States = [S0|_],
    ( foreach(X, S0), foreach(V, Init) do X #= V ),
    % the number of transfers, Cost: transfers 0 to Cost-1 are performed
    Cost :: 0..Max-1,
    % each transfer pours water from one bucket into another
    pours(States, 0, Caps, Cost, Fs, Tos),
    % after the goal state the states are fixed to 0 so that they stay determined (the padding that is printed is set in output_rows)
    zero_after(States, 0, Cost),
    % the goal state is reached after Cost transfers
    goal_at(States, 0, Goal, Cost),
    % the output rows: the states up to the goal, the padding value afterwards
    output_rows(States, 0, Cost, Pad, Caps, Seq),
    flatten(States, FlatStates),
    append([Cost|Fs], Tos, Head),
    append(Head, FlatStates, Vars),
    Outputs = [cost-Cost, sequence-Seq].

% the transfers between consecutive states: the source (F) and the target (To) bucket of each one
pours([_], _, _, _, [], []).
pours([S,N|Rest], Idx, Caps, Cost, [F|Fs], [To|Tos]) :-
    pour(Idx, S, N, Caps, Cost, F, To),
    Idx1 is Idx + 1,
    pours([N|Rest], Idx1, Caps, Cost, Fs, Tos).

% a transfer from bucket F to bucket To pours the smaller of the water the source holds and the room the target has.
% Transfers after the cost are not used, so their buckets are fixed.
pour(Idx, S, N, Caps, Cost, F, To) :-
    S = [S1,S2,S3], N = [N1,N2,N3],
    F :: 1..3, To :: 1..3,
    % a transfer goes from one bucket into another
    F #\= To,
    element(F, S, SrcV),
    element(To, S, DstV),
    element(To, Caps, CapTo),
    Amt #>= 0, Amt #=< CapTo,
    % the amount poured: the source is emptied or the target is filled, whichever comes first
    Amt #= min(SrcV, CapTo - DstV),
    F1 #= (F #= 1), F2 #= (F #= 2), F3 #= (F #= 3),
    T1 #= (To #= 1), T2 #= (To #= 2), T3 #= (To #= 3),
    % water moves out of the source bucket and into the target bucket
    (Idx #< Cost) => (N1 #= S1 - F1*Amt + T1*Amt),
    (Idx #< Cost) => (N2 #= S2 - F2*Amt + T2*Amt),
    (Idx #< Cost) => (N3 #= S3 - F3*Amt + T3*Amt),
    (Idx #>= Cost) => (F #= 1),
    (Idx #>= Cost) => (To #= 2).

% the states after the goal state are fixed to 0
zero_after([], _, _).
zero_after([S|Ss], Idx, Cost) :-
    S = [A,B,C],
    (Idx #> Cost) => (A #= 0),
    (Idx #> Cost) => (B #= 0),
    (Idx #> Cost) => (C #= 0),
    Idx1 is Idx + 1,
    zero_after(Ss, Idx1, Cost).

% the state after Cost transfers is the goal state
goal_at([], _, _, _).
goal_at([S|Ss], Idx, Goal, Cost) :-
    S = [A,B,C], Goal = [GA,GB,GC],
    (Cost #= Idx) => (A #= GA),
    (Cost #= Idx) => (B #= GB),
    (Cost #= Idx) => (C #= GC),
    Idx1 is Idx + 1,
    goal_at(Ss, Idx1, Goal, Cost).

% the output row of each state: the state up to the goal, the padding value afterwards
output_rows([], _, _, _, _, []).
output_rows([S|Ss], Idx, Cost, Pad, Caps, [Row|Rows]) :-
    S = [S1,S2,S3], Row = [O1,O2,O3], Caps = [Ca,Cb,Cc],
    O1 :: Pad..Ca, O2 :: Pad..Cb, O3 :: Pad..Cc,
    (Idx #=< Cost) => (O1 #= S1),
    (Idx #=< Cost) => (O2 #= S2),
    (Idx #=< Cost) => (O3 #= S3),
    (Idx #> Cost) => (O1 #= Pad),
    (Idx #> Cost) => (O2 #= Pad),
    (Idx #> Cost) => (O3 #= Pad),
    Idx1 is Idx + 1,
    output_rows(Ss, Idx1, Cost, Pad, Caps, Rows).

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
