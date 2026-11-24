% initials_queue: a MiniZinc model from DCP Rosetta.
%
% Ten people stand at the front of a queue for a Maths lecture. Each has initials that are an
% alphabetically ordered pair of distinct letters from the first five letters of the alphabet (A to E).
% No two people have the same initials, and no one shares a letter with the person in front of them.
% Mathematician BE is at the front of the queue, with CD right behind, and BD is at the end.
% Work out the initials of the ten people in the queue, starting from the front.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

int: n = 10;                                     % the number of people in the queue
set of int: Queue = 1..n;                        % positions in the queue, front first
set of int: Letters = 0..4;                      % the letters A to E, as 0 to 4
set of int: Positions = 1..2;                    % the two initials of a person

% queue[i, p]: the letter of initial p of the person at position i (0 = A, ..., 4 = E)
array[Queue, Positions] of var Letters: queue;

% the two initials of each person are in alphabetical order and distinct
constraint forall(i in Queue)(queue[i, 1] < queue[i, 2]);

% the initials of different people are different: code[i] identifies the pair of person i
array[Queue] of var 0..24: code;                 % code[i] = 5 * first + second
constraint forall(i in Queue)(code[i] = 5 * queue[i, 1] + queue[i, 2]);
constraint all_different(code);

% no one shares a letter with the person directly in front of them
constraint forall(i in 1..n - 1, p in Positions, q in Positions)(queue[i, p] != queue[i + 1, q]);

% BE (letters 1 and 4) is at the front of the queue
constraint queue[1, 1] = 1 /\ queue[1, 2] = 4;

% CD (letters 2 and 3) is right behind BE
constraint queue[2, 1] = 2 /\ queue[2, 2] = 3;

% BD (letters 1 and 3) is at the end of the queue
constraint queue[n, 1] = 1 /\ queue[n, 2] = 3;

solve satisfy;

output ["{\"queue\": ", showJSON(queue), "}"];
