Blind model, after reading the lessons of 20261016-maxicp-java-models (json:1 and json:2, the
16x16 decks whose containers fill the area exactly, timed out). Positions, a turned flag per
container, the separation disjunction per pair, and implied strip sums (the containers crossing
a unit strip fill at most, or with an exactly filled deck exactly, its length). Measured locally:
- with positions and flags as decisions: json:1 and json:2 time out at 120 s;
- with one Boolean per (cell, container), registered row by row from the bottom-left cell and
  tried "covers" first (a bottom-left packing order), still a timeout while a cell may stay empty;
- with every cell covered exactly once when the areas fill the deck (derived from the data):
  json:1 in 75 s, json:2 in 34 s, the rest under 15 s. That is this attempt.
Output conventions (right = left + extent across deck_width, top = bottom + extent along
deck_length, classes 1-based into separation) were accepted by evaluation.check first.
