# Swiss-Style Tournament Database

## Table of contents
- [What is it?](#what-is-it)
- [Features](#features)
- [What's included?](#what-s-included-)
- [Setup instructions](#setup-instructions)
- [Using the API](#using-the-api)
- [Example session](#example-session)
- [Running the unit tests](#running-the-unit-tests)
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

To use the tournament API, import the module into any Python file or into a Python interpreter session using `from tournament import *` (as always, insure `tournament.py` is in your working directory). The following functions are available:

- `registerPlayer(name, tournament_id=1)` - registers player with `name` for tournament with `tournament_id`
- `countPlayers(tournament_id=1)` - returns number of players registered for tournament with `tournament_id`
- `deletePlayers(tournament_id=1)` - deletes all players registered for tournament with `tournament_id`
- `deleteMatches(tournament_id=1)` - deletes all matches recorded for tournament with `tournament_id`
- `reportMatch(winner, loser, tournament_id=1, draw=False)` - records result of match between player with `winner` ID and player with `loser` ID for tournament with `tournament_id`. If draw is `True`, no wins or losses are recorded.
- `playerStandings(tournament_id=1)` - returns list of tuples containing ID, name, wins, and matches for a player each row.
- `def swissPairings(tournament_id=1)` - returns list of tuples for tournament with `tournament_id` following the form `(id1, name1, id2, name2)` where `id1` and `name1` is paired for a match with a player having `id2` and `name2`.

## Example session

Open a terminal window and type `python` to start the console interpreter and type the following:

    >>> from tournament import *
    
It is important that the path to the `tournament.py` file is specified in your `PYTHONPATH` environment variable. This will import the tournament API into the current environment. Next, let's register some players (for the sake of simplicity, we won't explicitly specify
a tournament ID and will instead use the default of 1).

    >>> registerPlayer("Flynn Taggart")
    >>> registerPlayer("B.J. Blazkowicz")
    
If we run `countPlayers()`, we will see we have two players registered for the tournament:

    >>> countPlayers()
    2

Just as we we would expect. And if we look at the standings:

    >>> playerStandings()
    [(1, 'Flynn Taggart', 0L, 0L), (2, 'B.J. Blazkowicz', 0L, 0L)]
    
We see that we have two players, each with no wins and no losses. Now let's try to report some match results. Let's say Flynn Taggart had a match against B.J. Blazkowicz, and the former won:

    >>> reportMatch(1, 2)
    >>> playerStandings()
    [(1, 'Flynn Taggart', 1L, 1L), (2, 'B.J. Blazkowicz', 0L, 1L)]
    
The standings reflect that Flynn Taggart now has one win and one match, compared with B.J. Blazkowicz's one match with no wins. Let's register a few more players and report some more match activity:

    >>> registerPlayer("Commander Keen")
    >>> registerPlayer("Dangerous Dave")
    >>> playerStandings()
    [(1, 'Flynn Taggart', 1L, 1L), (2, 'B.J. Blazkowicz', 0L, 1L), (3, 'Commander Keen', 0L, 0L), (4, 'Dangerous Dave', 0L, 0L)]
    >>> reportMatch(1, 3)
    >>> reportMatch(1, 4)
    >>> reportMatch(4, 3)
    >>> reportMatch(4, 2)
    >>> reportMatch(2, 3)
    >>> playerStandings()
    [(1, 'Flynn Taggart', 3L, 3L), (4, 'Dangerous Dave', 2L, 3L), (2, 'B.J. Blazkowicz', 1L, 3L), (3, 'Commander Keen', 0L, 3L)]
    
And if we take a look at the swiss pairings:

    >>> swissPairings()
    [(1, 'Flynn Taggart', 4, 'Dangerous Dave'), (2, 'B.J. Blazkowicz', 3, 'Commander Keen')]
    
We see that players with similar win counts are paired together.

## Running the unit tests

To run the unit tests, open up a terminal window and type:

`python tournament_test.py`

to run the basic unit tests, or:

`python extended_tests.py`

to run the more advanced unit tests.

## Thanks
Thanks for checking out my project. Have fun and enjoy!
