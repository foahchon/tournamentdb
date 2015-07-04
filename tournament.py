#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from tournament_exception import TournamentException


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id=1):
    """Remove all the match records from the database.

    Args:
      tournament_id: ID of tournament from which matches are being deleted

    """

    db_conn = connect()
    db_cursor = db_conn.cursor()

    db_cursor.execute("delete from matches "
                      "where tournament_id = %s;",
                      (tournament_id,))

    db_conn.commit()

    db_cursor.close()
    db_conn.close()


def deletePlayers(tournament_id=1):
    """Remove all the player records from the database.

    Args:
      tournament_id: ID of tournament from which players are being deleted
    """

    db_conn = connect()
    db_cursor = db_conn.cursor()

    db_cursor.execute("delete from players "
                      "where tournament_id = %s;",
                      (tournament_id,))

    db_conn.commit()

    db_cursor.close()
    db_conn.close()


def countPlayers(tournament_id=1):
    """Returns the number of players currently registered.

    Args:
        tournament_id: ID of tournament for which players are being counted
    """

    db_conn = connect()
    db_cursor = db_conn.cursor()

    db_cursor.execute("select count(*) from players where tournament_id = %s;",
                      (tournament_id,))

    player_count = db_cursor.fetchone()[0]  # Column 0 contains number of players.

    db_cursor.close()
    db_conn.close()

    return int(player_count)  # Convert to int before returning.


def registerPlayer(name, tournament_id=1):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
      tournament_id: ID of tournament player is registering for
    """

    db_conn = connect()
    db_cursor = db_conn.cursor()

    db_cursor.execute("insert into players (name, tournament_id) values (%s, %s);",
                      (name, tournament_id))

    db_conn.commit()

    db_cursor.close()
    db_conn.close()

    _assignBye(tournament_id)


def playerStandings(tournament_id=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament_id: ID of tournament for which standings are being compiled

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db_conn = connect()
    db_cursor = db_conn.cursor()

    db_cursor.execute("select ps.id, ps.name, ps.wins, ps.matches from "
                      "(select * from player_standings where tournament_id = %s) ps;",
                      (tournament_id,))

    results = db_cursor.fetchall()

    db_cursor.close()
    db_conn.close()

    return results


def reportMatch(winner, loser, tournament_id=1, draw=False):
    """Records the outcome of a single match between two players.
    If draw is True, no wins or losses are recorded.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tournament_id: ID of tournament match belongs to
      draw: boolean value indicating whether result of match was a draw
    """

    if not draw:
        db_conn = connect()
        db_cursor = db_conn.cursor()

        # Select player rows to ensure players are in the correct tournament.
        db_cursor.execute("select tournament_id from players where id = %s or id = %s;",
                          (winner, loser))

        player_rows = db_cursor.fetchall()

        # Make sure that winner and loser are not equal, that both players are registered
        # for the correct tournament.
        if winner != loser and (db_cursor.rowcount != 2
                                or player_rows[0][0] != tournament_id
                                or player_rows[1][0] != tournament_id):
            raise TournamentException("Both players must exist and be registered for the correct tournament.")

        # Ensure that players have not already played each other.
        db_cursor.execute("select count(*) from matches "
                          "where winner_id = %(winner)s and loser_id = %(loser)s "
                          "or winner_id = %(loser)s and loser_id = %(winner)s;",
                          {'winner': winner, 'loser': loser})

        if db_cursor.fetchone()[0] != 0:
            raise TournamentException("Players can only have played each other once.")

        db_cursor.execute("insert into matches (winner_id, loser_id, tournament_id) "
                          "values (%s, %s, %s);",
                          (winner, loser, tournament_id))

        db_conn.commit()

        db_cursor.close()
        db_conn.close()


def swissPairings(tournament_id=1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament_id: ID of tournament for which pairings are being compiled
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    standings = playerStandings(tournament_id)

    results = []

    # Player standings are already sorted by wins, so just select pairs
    # from rows returned by playerStandings() function. Player in last place
    # is not paired.
    for i in range(0, len(standings) - 1, 2):
        results.append((standings[i][0], standings[i][1],
                        standings[i + 1][0], standings[i + 1][1]))

    return results


def _assignBye(tournament_id=1):
    """Assigns a bye on tournaments with odd number of players, increasing
    player's record by 1 win and 1 match. If a tournament has an even number
    of players, the bye is revoked.

    Args:
      tournament_id: tournament ID which bye may be assigned to
    """
    db_conn = connect()
    db_cursor = db_conn.cursor()

    # If number of players registered for a given tournament is odd, assign
    # a bye. Otherwise, revoke any previously assigned bye by deleting from
    # the assigned_byes table.
    if countPlayers(tournament_id) % 2 != 0:
        # Bye is automatically assigned to the lowest player ID.
        db_cursor.execute("select id from players "
                          "where tournament_id = %s "
                          "order by id limit 1;",
                          (tournament_id,))

        player_id = db_cursor.fetchone()[0]

        db_cursor.execute("insert into assigned_byes "
                          "(tournament_id, player_id) values (%s, %s);",
                          (tournament_id, player_id))
    else:
        db_cursor.execute("delete from assigned_byes "
                          "where tournament_id = %s;",
                          (tournament_id,))

    db_conn.commit()

    db_cursor.close()
    db_conn.close()
