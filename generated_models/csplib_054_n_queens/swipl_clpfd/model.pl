% csplib_054_n_queens: a SWI-Prolog model from DCP Rosetta.
%
% Can n queens (of the same color) be placed on an n x n chessboard so that none of the queens can attack each
% other? A queen attacks the squares on the same row, column, or either diagonal as itself, so the n-queens problem
% is to find a set of n locations on a chessboard, no two of which are on the same row, column or diagonal.
%
% Save this file as model.pl. Download `csplib_054_n_queens.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_054_n_queens.json')" -t halt model.pl
%
% Data fields: n (the size of the board, which is also the number of queens).
:- use_module(library(clpfd)).

model(Instance, [Queens, Downs, Ups], [queens-Queens]) :-
    N = Instance.n,
    length(Queens, N),                  % one queen per row: Queens[I] is the column of the queen in row I
    Queens ins 1..N,
    numlist(1, N, Rows),
    % the diagonal index of each queen, going down and going up the board
    maplist([Q, R, D]>>(D #= Q - R), Queens, Rows, Downs),
    maplist([Q, R, U]>>(U #= Q + R), Queens, Rows, Ups),
    % no two queens in the same column
    all_distinct(Queens),
    % no two queens on the same diagonal
    all_distinct(Downs),
    all_distinct(Ups).

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
