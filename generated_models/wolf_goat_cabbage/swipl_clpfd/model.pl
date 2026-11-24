% wolf_goat_cabbage: a SWI-Prolog model from DCP Rosetta.
%
% The wolf, goat and cabbage problem is a river crossing puzzle. A farmer with a wolf, a goat, and a cabbage must
% cross a river by boat. The boat can carry only the farmer and a single item. If left unattended together, the wolf
% would eat the goat, or the goat would eat the cabbage. How can they cross the river without anything being eaten?
%
% The crossing takes the given number of stages. At the first stage everything is on the starting shore, at the last
% stage everything is on the destination shore, and the boat, with the farmer, changes shore from each stage to the
% next.
%
% Save this file as model.pl. Download `wolf_goat_cabbage.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('wolf_goat_cabbage.json')" -t halt model.pl
%
% Data fields: stage (the number of stages, including the first and the last).
:- use_module(library(clpfd)).

model(Instance, Vars, [wolf_pos-Wolf, goat_pos-Goat, cabbage_pos-Cabbage, boat_pos-Boat]) :-
    Stages = Instance.stage,
    length(Wolf, Stages),                 % Wolf[S] = 1 when the wolf is on the destination shore at stage S
    length(Goat, Stages),
    length(Cabbage, Stages),
    length(Boat, Stages),
    append([Wolf, Goat, Cabbage, Boat], Vars),
    Vars ins 0..1,
    % at the first stage everything is on the starting shore (0)
    Wolf = [0|_], Goat = [0|_], Cabbage = [0|_], Boat = [0|_],
    % at the last stage everything is on the destination shore (1)
    last(Wolf, 1), last(Goat, 1), last(Cabbage, 1), last(Boat, 1),
    % at every stage, the wolf is never left alone with the goat, nor the goat with the cabbage
    safe_stages(Wolf, Goat, Cabbage, Boat),
    % from each stage to the next, the boat crosses, carrying the farmer and at most one item
    crossings(Wolf, Goat, Cabbage, Boat).

% If the wolf and the goat share a shore, the farmer is there too; likewise the goat and the cabbage.
safe_stages([], [], [], []).
safe_stages([W|Ws], [G|Gs], [C|Cs], [B|Bs]) :-
    (G #= W) #==> (B #= W),
    (G #= C) #==> (B #= G),
    safe_stages(Ws, Gs, Cs, Bs).

% Each crossing: the boat changes shore, at most one item changes shore with it, and an item changes shore only when
% it is on the boat's shore before the crossing.
crossings([_], [_], [_], [_]).
crossings([W1, W2|Ws], [G1, G2|Gs], [C1, C2|Cs], [B1, B2|Bs]) :-
    B1 #\= B2,
    abs(W1 - W2) + abs(G1 - G2) + abs(C1 - C2) #=< 1,
    (W1 #\= W2) #==> (B1 #= W1),
    (G1 #\= G2) #==> (B1 #= G1),
    (C1 #\= C2) #==> (B1 #= C1),
    crossings([W2|Ws], [G2|Gs], [C2|Cs], [B2|Bs]).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
