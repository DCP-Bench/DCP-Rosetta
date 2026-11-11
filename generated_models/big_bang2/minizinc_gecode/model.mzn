% big_bang2: a MiniZinc model from DCP Rosetta.
%
% Nontransitive dice: find five dice, one for each of Rock, Paper, Scissors, Lizard and Spock, such that
% the dominance relationships between the dice are those of Rock-Paper-Scissors extended by Lizard and
% Spock. Each choice beats two other choices and is beaten by two other choices:
%   Rock crushes Scissors and Lizard; Paper covers Rock and disproves Spock; Scissors cuts Paper and
%   decapitates Lizard; Lizard eats Paper and poisons Spock; Spock vaporizes Rock and smashes Scissors.
% Each die has six integer faces, each between 1 and 12 inclusive. Faces may repeat, within a die and
% across dice. A die A beats a die B if A has a strictly larger face value than B in more than half of
% all pairs of faces.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: num_dice = 5;                            % Rock, Paper, Scissors, Lizard, Spock
int: faces = 6;                               % faces on each die
int: max_value = 12;                          % the largest face value

int: Rock = 0;
int: Paper = 1;
int: Scissors = 2;
int: Lizard = 3;
int: Spock = 4;

set of int: Dice = 0..num_dice-1;             % the dice, in the order Rock, Paper, Scissors, Lizard, Spock
set of int: Face = 1..faces;                  % the faces of a die
set of int: Values = 1..max_value;            % the face values

% the ten beats relations, as (winner, loser) pairs
int: num_beats = 10;
array[1..num_beats, 1..2] of int: beats = array2d(1..num_beats, 1..2, [
    Rock, Scissors,     Rock, Lizard,       Paper, Rock,        Paper, Spock,       Scissors, Paper,
    Scissors, Lizard,   Lizard, Paper,      Lizard, Spock,      Spock, Rock,        Spock, Scissors
]);

% dice[d, f]: the value on face f of die d
array[Dice, Face] of var Values: dice;

% helper counts, determined by dice: how many faces of die d show value v, and how many show less than v
array[Dice, Values] of var 0..faces: faces_with;
array[Dice, Values] of var 0..faces: faces_below;

constraint forall(d in Dice)(global_cardinality([dice[d, f] | f in Face], Values, [faces_with[d, v] | v in Values]));
constraint forall(d in Dice, v in Values)(faces_below[d, v] = sum(w in 1..v-1)(faces_with[d, w]));

% each beats relation holds: the winner has a strictly larger face in more than half of the 36 face pairs
constraint forall(k in 1..num_beats)(
    sum(v in Values)(faces_with[beats[k, 1], v] * faces_below[beats[k, 2], v]) > (faces * faces) div 2);

solve satisfy;
output ["{\"dice\": ", showJSON(dice), "}"];
