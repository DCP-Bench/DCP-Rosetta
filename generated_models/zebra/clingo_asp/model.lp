% zebra: a clingo model from DCP Rosetta.
%
% The Zebra puzzle (sometimes referred to as Einstein's puzzle) is defined as follows.
% There are five houses in a row, numbered from left to right.
% Each of the five houses is painted a different color, and has one inhabitant.
% The inhabitants are all of different nationalities, own different pets, drink different beverages and have different jobs.
% We know that:
%  - colors are yellow, green, red, white, and blue
%  - nations of inhabitants are italy, spain, japan, england, and norway
%  - pets are cat, zebra, bear, snails, and horse
%  - drinks are milk, water, tea, coffee, and juice
%  - jobs are painter, sculptor, diplomat, pianist, and doctor
%  - the painter owns the horse
%  - the diplomat drinks coffee
%  - the one who drinks milk lives in the white house
%  - the Spaniard is a painter
%  - the Englishman lives in the red house
%  - the snails are owned by the sculptor
%  - the green house is immediately on the left of the red one
%  - the Norwegian lives immediately on the right of the blue house
%  - the doctor drinks milk
%  - the diplomat is Japanese
%  - the Norwegian owns the zebra
%  - the green house is next to the white one
%  - the horse is owned by the neighbor of the diplomat
%  - the Italian either lives in the red, white or green house
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

house(0..4).

% the values of each attribute, numbered in the order the puzzle lists them
#const yellow = 0.
#const green = 1.
#const red = 2.
#const white = 3.
#const blue = 4.
#const italy = 0.
#const spain = 1.
#const japan = 2.
#const england = 3.
#const norway = 4.
#const cat = 0.
#const zebra = 1.
#const bear = 2.
#const snails = 3.
#const horse = 4.
#const milk = 0.
#const water = 1.
#const tea = 2.
#const coffee = 3.
#const juice = 4.
#const painter = 0.
#const sculptor = 1.
#const diplomat = 2.
#const pianist = 3.
#const doctor = 4.

color(0..4).
nation(0..4).
pet(0..4).
drink(0..4).
job(0..4).

% each attribute value is in exactly one house, and each house has exactly one value of each attribute
1 { colors(C, H) : house(H) } 1 :- color(C).
1 { colors(C, H) : color(C) } 1 :- house(H).
1 { nations(N, H) : house(H) } 1 :- nation(N).
1 { nations(N, H) : nation(N) } 1 :- house(H).
1 { pets(P, H) : house(H) } 1 :- pet(P).
1 { pets(P, H) : pet(P) } 1 :- house(H).
1 { drinks(D, H) : house(H) } 1 :- drink(D).
1 { drinks(D, H) : drink(D) } 1 :- house(H).
1 { jobs(J, H) : house(H) } 1 :- job(J).
1 { jobs(J, H) : job(J) } 1 :- house(H).

% the painter owns the horse
:- pets(horse, H), not jobs(painter, H).

% the diplomat drinks coffee
:- jobs(diplomat, H), not drinks(coffee, H).

% the one who drinks milk lives in the white house
:- drinks(milk, H), not colors(white, H).

% the Spaniard is a painter
:- nations(spain, H), not jobs(painter, H).

% the Englishman lives in the red house
:- nations(england, H), not colors(red, H).

% the snails are owned by the sculptor
:- pets(snails, H), not jobs(sculptor, H).

% the green house is immediately on the left of the red one
:- colors(green, H), not colors(red, H + 1).

% the Norwegian lives immediately on the right of the blue house
:- nations(norway, H), not colors(blue, H - 1).

% the doctor drinks milk
:- jobs(doctor, H), not drinks(milk, H).

% the diplomat is Japanese
:- jobs(diplomat, H), not nations(japan, H).

% the Norwegian owns the zebra
:- nations(norway, H), not pets(zebra, H).

% the green house is next to the white one
:- colors(green, H), not colors(white, H - 1), not colors(white, H + 1).

% the horse is owned by the neighbor of the diplomat
:- pets(horse, H), jobs(diplomat, D), |H - D| != 1.

% the Italian either lives in the red, white or green house
:- nations(italy, H), colors(C, H), C != red, C != white, C != green.

#show colors/2.
#show nations/2.
#show pets/2.
#show drinks/2.
#show jobs/2.
