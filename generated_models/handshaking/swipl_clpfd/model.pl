% handshaking: a SWI-Prolog model from DCP Rosetta.
%
% Hilary and Jocelyn are married. They invite a number of couples who are friends for dinner. When they arrive,
% they shake hands with each other. Nobody shakes hands with him or herself or with his or her spouse. After there
% has been some handshaking, Jocelyn jumps up on a chair and says 'Stop shaking hands!', and then asks how many
% hands each person has shaken. All the answers are different. How many hands has Hilary shaken?
%
% Save this file as model.pl. Download `handshaking.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('handshaking.json')" -t halt model.pl
%
% Data fields: num_couples (the number of invited couples, besides the two hosts).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Vars, [hil-Hil]) :-
    NumCouples = Instance.num_couples,
    N is 2 + 2 * NumCouples,               % the people at the party: the two hosts and the invited couples
    MaxHands is N - 2,                     % nobody shakes hands with self or with the spouse
    % Hands[P] is the number of hands person P has shaken. Person 1 is Hilary, person 2 is Jocelyn, and the
    % guests follow couple by couple: persons 2C-1 and 2C are the two members of couple C.
    length(Hands, N),
    Hands ins 0..MaxHands,
    Hands = [Hil, _Jocelyn|Guests],
    % Jocelyn asks everybody else, so the answers of everybody except Jocelyn are all different
    all_distinct([Hil|Guests]),
    % Shake[P][Q] is 1 when persons P and Q shake hands
    length(Shake, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Shake),
    numlist(1, N, People),
    findall(P-Q, (member(P, People), member(Q, People), P < Q), Pairs),
    % a handshake is mutual: Shake[P][Q] and Shake[Q][P] are the same variable
    maplist(mutual(Shake), Pairs),
    % nobody shakes their own hand
    maplist(no_self(Shake), People),
    % nobody shakes hands with their spouse
    Couples is N // 2,
    numlist(1, Couples, CoupleNumbers),
    maplist(no_spouse(Shake), CoupleNumbers),
    % the number of hands a person has shaken is the number of people in their row of handshakes
    maplist(hands_of, Shake, Hands),
    % symmetry breaking: the guests of a couple can swap names, and couples can swap places, without changing
    % what Hilary shook; fix the order of the couples by the count of their first member
    guest_order(Guests),
    Vars = [Hands, Shake].

% mutual(+Shake, +Pair): the handshake between P and Q is the same entry in both directions
mutual(Shake, P-Q) :-
    cell(Shake, P, Q, Cell),
    cell(Shake, Q, P, Cell).

% no_self(+Shake, +P): person P does not shake their own hand
no_self(Shake, P) :-
    cell(Shake, P, P, 0).

% no_spouse(+Shake, +C): the two members of couple C, persons 2C-1 and 2C, do not shake hands
no_spouse(Shake, C) :-
    A is 2 * C - 1,
    B is 2 * C,
    cell(Shake, A, B, 0).

% hands_of(+Row, -Count): Count is the number of handshakes in the row of one person
hands_of(Row, Count) :-
    sum(Row, #=, Count).

% cell(+Matrix, +I, +J, ?Value): Value is entry (I, J) of the matrix, counting from 1
cell(Matrix, I, J, Value) :-
    nth1(I, Matrix, Row),
    nth1(J, Row, Value).

% guest_order(+Counts): Counts lists the guests couple by couple; each couple's first count is below its second
% and below the first count of the next couple
guest_order([]).
guest_order([First, Second|Rest]) :-
    First #< Second,
    (   Rest = [NextFirst|_]
    ->  First #< NextFirst
    ;   true
    ),
    guest_order(Rest).

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
