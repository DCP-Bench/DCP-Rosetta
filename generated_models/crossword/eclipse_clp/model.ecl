% crossword: an ECLiPSe model from DCP Rosetta.
%
% Complete a 6 by 5 crossword puzzle, with some blocked cells, from a list of 15 words: select
% 8 of the words such that the puzzle can be completed. Each numbered position starts one entry
% (an across or a down word) that takes a word of its length, and the letters of two entries
% agree where they cross. The words are sorted from the longest, then alphabetically.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).
:- lib(listut).

% The 15 words, in sorted order: word 0 is HOSES, word 14 is TIE.
words(["HOSES", "LASER", "SAILS", "SHEET", "STEER",
       "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
       "AFT", "ALE", "EEL", "LEE", "TIE"]).

model(_Instance, Vars, ['E'-Index]) :-
    words(Words),
    length(Words, NumWords),
    % the length of each word, and for each position 1 to 5 the letter of every word there
    ( foreach(Word, Words), foreach(WordLength, Lengths) do string_length(Word, WordLength) ),
    ( for(Pos, 1, 5), foreach(Col, Columns), param(Words) do
        letter_column(Words, Pos, Col)
    ),
    % the open cells of the puzzle, row by row (the blocked cells are left out)
    Letters = [C11, C12, C13, C14, C15,
               C23, C25,
               C32, C33, C34, C35,
               C41, C43, C44, C45,
               C51, C52, C53, C54, C55,
               C61, C64],
    Letters :: 65..90,
    % the entries of the puzzle, for the numbers 1 to 8 in order:
    % 1 across, 2 down, 3 down, 4 across, 5 down, 6 down, 7 across, 8 across
    Entries = [[C11, C12, C13, C14, C15],
               [C13, C23, C33, C43, C53],
               [C15, C25, C35, C45, C55],
               [C32, C33, C34, C35],
               [C34, C44, C54, C64],
               [C41, C51, C61],
               [C43, C44, C45],
               [C51, C52, C53, C54, C55]],
    % select 8 of the 15 words, each word used for at most one entry
    % element/3 counts from 1, so a chosen word is numbered 1 to 15 here and
    % its index in the output is that number minus 1
    length(Chosen, 8),
    Chosen :: 1..NumWords,
    alldifferent(Chosen),
    length(Index, 8),
    ( foreach(C, Chosen), foreach(I, Index) do I #= C - 1 ),
    % each entry takes a word of its own length, and the letters of the chosen word
    % fill the cells of the entry in order
    ( foreach(Cells, Entries), foreach(Choice, Chosen), param(Lengths, Columns) do
        length(Cells, Size),
        element(Choice, Lengths, Size),
        ( for(Pos, 1, Size), param(Cells, Choice, Columns) do
            nth1(Pos, Cells, Cell),
            nth1(Pos, Columns, Col),
            element(Choice, Col, Cell)
        )
    ),
    append(Chosen, Letters, Vars).

% the J-th letter (as a character code) of each word, 0 when the word is shorter than J
letter_column(Words, J, Column) :-
    ( foreach(S, Words), foreach(C, Column), param(J) do
        string_list(S, Codes),
        ( nth1(J, Codes, C0) -> C = C0 ; C = 0 )
    ).

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
