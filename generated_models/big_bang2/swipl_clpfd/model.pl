% big_bang2: a SWI-Prolog model from DCP Rosetta.
%
% Nontransitive dice: find five dice, each with six faces whose values are whole numbers from 1 to 12 (faces may
% repeat, within a die and across dice), such that the "beats" relation between the dice is the relation of the game
% Rock-Paper-Scissors-Lizard-Spock: Rock beats Scissors and Lizard; Paper beats Rock and Spock; Scissors beats Paper
% and Lizard; Lizard beats Paper and Spock; Spock beats Rock and Scissors. A die A beats a die B when A has a strictly
% larger face than B in more than half of all pairs of faces.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% The model reads no data. Dice lists the faces of each die, in the order Rock, Paper, Scissors, Lizard, Spock.
model(_Instance, Vars, [dice-Dice]) :-
    Dice = [Rock, Paper, Scissors, Lizard, Spock],
    % each die has six faces, each a whole number from 1 to 12
    maplist(die_faces, Dice),
    % search guidance, not part of the statement: all dice have the same total Total over their faces
    % (solutions exist; it makes the search far shorter)
    Total in 6..72,
    maplist(sum_is(Total), Dice),
    % Less[V] = number of faces of the die that are smaller than V, for V = 1..12
    maplist(smaller_counts, Dice, [LR, LP, LS, LL, LK]),
    % the ten beats relationships: the first die beats the second
    beats(Rock, LS), beats(Rock, LL),
    beats(Paper, LR), beats(Paper, LK),
    beats(Scissors, LP), beats(Scissors, LL),
    beats(Lizard, LP), beats(Lizard, LK),
    beats(Spock, LR), beats(Spock, LS),
    % labelling order: Rock, Scissors, Lizard, Paper, Spock, so that each die is fixed
    % next to the dice it is compared with
    append([Rock, Scissors, Lizard, Paper, Spock, [Total]], Vars).

% A die has six faces, each from 1 to 12. The faces of a die are a set, so they are listed in ascending order,
% which breaks the symmetry.
die_faces(Faces) :-
    length(Faces, 6),
    Faces ins 1..12,
    chain(Faces, #=<).

% Less[V] = number of faces of the die that are smaller than V, for V = 1..12
smaller_counts(Faces, Less) :-
    length(Less, 12),
    numlist(1, 12, Values),
    maplist(count_smaller(Faces), Values, Less).

count_smaller(Faces, V, Count) :-
    smaller_flags(Faces, V, Flags),
    sum(Flags, #=, Count).

smaller_flags([], _, []).
smaller_flags([F|Fs], V, [B|Bs]) :-
    B #<==> (F #< V),
    smaller_flags(Fs, V, Bs).

% Die A beats die B when A has a strictly larger face than B in at least 19 of the 36 pairs of faces.
beats(A, LessB) :-
    maplist(wins_of_face(LessB), A, Wins),
    sum(Wins, #>=, 19).

% number of faces of the other die that are smaller than face X
wins_of_face(LessB, X, W) :-
    element(X, LessB, W).

sum_is(Total, Faces) :- sum(Faces, #=, Total).

labeling_options([leftmost, up]).

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
