% initials_queue: a clingo model from DCP Rosetta.
%
% The first 10 people in the queue for a Maths lecture each have initials that are an alphabetically
% ordered pair of distinct letters from the first five letters of the alphabet (A to E). None of them has
% the same initials as any other, and no-one shares a letter with the person in front of them. The
% mathematician BE is at the front of the queue with CD right behind, and BD is right at the end of the
% queue. Work out the initials of the ten people in the queue, starting from the front.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the letters A to E are 0 to 4, the people in the queue are 0 to 9 (front first), and each person's
% initials have two slots, the first letter (0) and the second letter (1)
letter(0..4).
spot(0..9).
slot(0..1).

% queue(P, S, L): the letter L is in slot S of the initials of the person at spot P
1 { queue(P,S,L) : letter(L) } 1 :- spot(P), slot(S).

% the initials of each person are two distinct letters in alphabetical order
:- queue(P,0,X), queue(P,1,Y), X >= Y.

% no two people have the same initials
:- queue(P,0,X), queue(P,1,Y), queue(Q,0,X), queue(Q,1,Y), P < Q.

% no-one shares a letter with the person in front of them
:- queue(P,_,L), queue(Q,_,L), Q == P + 1.

% BE is at the front of the queue
:- not queue(0,0,1).
:- not queue(0,1,4).

% CD is right behind BE
:- not queue(1,0,2).
:- not queue(1,1,3).

% BD is right at the end of the queue
:- not queue(9,0,1).
:- not queue(9,1,3).

#show queue/3.
