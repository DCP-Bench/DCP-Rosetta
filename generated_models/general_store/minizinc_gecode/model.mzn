% general_store: a MiniZinc model from DCP Rosetta.
%
% The owner of a general store, who is something of a puzzlist, has put up a sign: the words above
% the horizontal line, read as numbers, add up to the total ALL WOOL. Each different letter stands
% for a different digit. Change all the letters to the correct digits. Leading zeros are allowed: a
% word may start with the digit 0. The sixteen words above the line are
%   CHESS CASH BOWWOW CHOPS ALSOPS PALEALE COOL BASS HOPS ALES HOES APPLES COWS CHEESE CHSOAP SHEEP
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

enum Letter = {A, B, C, E, H, L, O, P, S, W};   % the letters of the puzzle

% digit[l]: the digit that letter l stands for
array[Letter] of var 0..9: digit;

% each letter stands for a different digit
constraint all_different([digit[l] | l in Letter]);

% the number a word stands for: its letters, read as decimal digits, most significant first
function var int: value(array[int] of Letter: word) =
    sum(i in index_set(word))(pow(10, card(index_set(word)) - i) * digit[word[i]]);

array[int] of Letter: CHESS = [C, H, E, S, S];
array[int] of Letter: CASH = [C, A, S, H];
array[int] of Letter: BOWWOW = [B, O, W, W, O, W];
array[int] of Letter: CHOPS = [C, H, O, P, S];
array[int] of Letter: ALSOPS = [A, L, S, O, P, S];
array[int] of Letter: PALEALE = [P, A, L, E, A, L, E];
array[int] of Letter: COOL = [C, O, O, L];
array[int] of Letter: BASS = [B, A, S, S];
array[int] of Letter: HOPS = [H, O, P, S];
array[int] of Letter: ALES = [A, L, E, S];
array[int] of Letter: HOES = [H, O, E, S];
array[int] of Letter: APPLES = [A, P, P, L, E, S];
array[int] of Letter: COWS = [C, O, W, S];
array[int] of Letter: CHEESE = [C, H, E, E, S, E];
array[int] of Letter: CHSOAP = [C, H, S, O, A, P];
array[int] of Letter: SHEEP = [S, H, E, E, P];
array[int] of Letter: ALLWOOL = [A, L, L, W, O, O, L];

% the sixteen words above the line add up to ALL WOOL
constraint value(CHESS) + value(CASH) + value(BOWWOW) + value(CHOPS) + value(ALSOPS) + value(PALEALE)
         + value(COOL) + value(BASS) + value(HOPS) + value(ALES) + value(HOES) + value(APPLES)
         + value(COWS) + value(CHEESE) + value(CHSOAP) + value(SHEEP) = value(ALLWOOL);

solve satisfy;

output ["{\"C\": ", showJSON(digit[C]), ", \"H\": ", showJSON(digit[H]), ", \"E\": ", showJSON(digit[E]),
        ", \"S\": ", showJSON(digit[S]), ", \"A\": ", showJSON(digit[A]), ", \"B\": ", showJSON(digit[B]),
        ", \"O\": ", showJSON(digit[O]), ", \"W\": ", showJSON(digit[W]), ", \"P\": ", showJSON(digit[P]),
        ", \"L\": ", showJSON(digit[L]), "}"];
