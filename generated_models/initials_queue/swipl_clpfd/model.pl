% initials_queue: a SWI-Prolog model from DCP Rosetta.
%
% The first 10 people in the queue for a Maths lecture each have initials which are an alphabetically ordered pair
% of distinct letters from the first five letters of the alphabet (A to E). None of them has the same initials as
% any other, and nobody shares a letter with the person in front of them. Mathematician BE is at the front of the
% queue with CD right behind, and BD is right at the end of the queue. Work out the initials of the ten people in
% the queue, starting from the front. Letters are coded 0 to 4 for A to E.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% Data fields: none, the problem has no data; the model reads nothing from the instance.
:- use_module(library(clpfd)).
:- use_module(library(lists)).

model(_Instance, Vars, [queue-Queue]) :-
    Size = 10,                             % the number of people in the queue
    length(Queue, Size),
    % each person's initials are a pair [First, Second] of letters from 0 to 4, in alphabetical order
    maplist(initials, Queue),
    Vars = Queue,
    % no two people have the same initials
    maplist(code, Queue, Codes),
    all_different(Codes),
    % nobody shares a letter with the person in front of them
    queue_chain(Queue),
    % BE is at the front, then CD right behind it
    Queue = [[1, 4], [2, 3]|_],
    % BD is at the end of the queue
    last(Queue, [1, 3]).

% initials(?Pair): the two letters of a person, in alphabetical order and distinct
initials([First, Second]) :-
    [First, Second] ins 0..4,
    First #< Second.

% code(+Pair, -Code): a number identifying the pair of letters
code([First, Second], Code) :-
    Code #= 5 * First + Second.

% queue_chain(+Queue): each person has no letter in common with the next person
queue_chain([_]).
queue_chain([Front, Behind|Rest]) :-
    no_common_letter(Front, Behind),
    queue_chain([Behind|Rest]).

% no_common_letter(+Pair1, +Pair2): the two pairs of letters share no letter
no_common_letter([A, B], [C, D]) :-
    A #\= C,
    A #\= D,
    B #\= C,
    B #\= D.

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).

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
