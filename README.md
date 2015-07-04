# Swiss-Style Tournament Database

##Table of contents
- [What is it?](#what-is-it)
- [Features](#features)
- [What's included?](#what-s-included-)
- [Setup instructions](#setup-instructions)
- [Using the API](#using-the-api)
- [Thanks](#thanks)

## What is it?

A swiss-style tournament database configuration with corresponding API for player registration, match result reporting, and standings. Multiple tournaments can be created and deleted within a single database.

## Features

- Multiple tournaments within the same database.
- Results from multiple matches between the same two players are prevented.
- Byes are assigned in tournaments with an odd number of players.
- In standings, ties in records between players are broken by OWM (number of wins divided by number of opponents).

## What's included?
- `tournament.sql` - contains SQL database instructions for a PostgreSQL database server
- `tournament.py` - contains API definition for registering players, reporting matches, viewing current standings, etc.
- `tournament_exception.py` - contains class definition for custom exception `TournamentException`, for use where exceptions relating to tournament rules are raised.
- `tournament_test.py` - contains unit tests for basic database functionality
- `extended_tests.py` - contains unit tests for more advanced features of database (support for multiple tournaments, tie-breaking, rematch prevention, etc.) in addition to basic functionality.

## Setup instructions

To setup the database, simply open up a terminal window and type:

`psql -f tournament.sql`

Ensure that the `tournament.sql` file is in your current working directory and that PostgreSQL is installed on your machine. Running this file will connect to a database on the server called `tournament` and create the necessary tables and views for use with the API.

## Using the API

To use the tournament API, import the module into any Python file. The following functions are available:

- `registerPlayer(name, tournament_id=1)` - registers player with `name` for tournament `tournament_id`
- `countPlayers(tournament_id=1)` - returns number of players registered for tournament `tournament_id`
- `deletePlayers(tournament_id=1)` - deletes all players registered for tournament `tournament_id`
- `deleteMatches(tournament_id=1)` - deletes all matches recorded for tournament `tournament_id`
- `reportMatch(winner, loser, tournament_id=1, draw=False)` - records result of match between `winner` and `loser`. If draw is `True`, no wins or losses are recorded.
- `playerStandings(tournament_id=1)` - returns list of tuples containing ID, name, wins, and matches for a player each row.
- `def swissPairings(tournament_id=1)` - returns pairings of players for the next round of a tournament.

## Thanks
Thanks for checking out my project. Have fun and enjoy!
