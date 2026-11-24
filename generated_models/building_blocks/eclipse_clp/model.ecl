% building_blocks: an ECLiPSe model from DCP Rosetta.
%
% Each of a number of alphabet blocks has a single letter of the alphabet on each of its sides, and each block has the same
% number of sides. In all, the blocks contain every letter of the alphabet but Q and Z, and each letter is on exactly one
% block. By arranging the blocks in various ways, all the words of a given list can be spelled, using each block for at most
% one letter of a word, so the letters of a word are all on different blocks. Find the block on which each letter of the
% alphabet is placed, numbered from 0.
%
% Save this file as model.ecl. Download `building_blocks.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py building_blocks.json
%   eclipse -b model.ecl -e "run('building_blocks_1.dat'), halt"

% Fields read: num_blocks is the number of blocks, num_sides the number of sides of each block, num_letters the number
% of letters, alphabet the string of the letters, words_str the list of the words to spell.

:- lib(ic).
:- lib(listut).

% the position of a character code in the list of codes of the alphabet
code_index(Code, Codes, I) :- nth1(I, Codes, C), C == Code, !.

% Output dice: the block of each letter of the alphabet, in the order of the letters.
model(Instance, Blocks, [dice-Blocks]) :-
    memberchk(num_blocks-NumBlocks, Instance),
    memberchk(num_sides-NumSides, Instance),
    memberchk(num_letters-NumLetters, Instance),
    memberchk(alphabet-Alphabet, Instance),
    memberchk(words_str-Words, Instance),
    string_list(Alphabet, AlphabetCodes),
    length(Blocks, NumLetters),
    Last is NumBlocks - 1,
    Blocks :: 0..Last,
    % each block has the same number of sides, one letter on each side
    ( for(B, 0, Last), param(Blocks, NumSides) do
        ( foreach(X, Blocks), foreach(Bool, Bools), param(B) do
            Bool #= (X #= B)
        ),
        sum(Bools) #= NumSides
    ),
    % the letters of each word are all on different blocks
    ( foreach(Word, Words), param(AlphabetCodes, Blocks) do
        string_list(Word, Codes),
        ( foreach(Code, Codes), foreach(X, Xs), param(AlphabetCodes, Blocks) do
            code_index(Code, AlphabetCodes, I),
            nth1(I, Blocks, X)
        ),
        alldifferent(Xs)
    ).

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
