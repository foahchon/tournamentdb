#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from tournament_exception import TournamentException


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    db_conn = psycopg2.connect("dbname={}".format(database_name))
    db_cursor = db_conn.cursor()

    return db_conn, db_cursor


def deleteMatches(tournament_id=1):
    """Remove all the match records from the database.

    Args:
      tournament_id: ID of tournament from which matches are being deleted

    """

    db_conn, db_cursor = connect()

    query = "DELETE FROM matches " \
            "WHERE tournament_id = %s;"

    params = (tournament_id,)

    db_cursor.execute(query, params)
    db_conn.commit()

    _closeDb(db_conn, db_cursor)


def deletePlayers(tournament_id=1):
    """Remove all the player records from the database.

    Args:
      tournament_id: ID of tournament from which players are being deleted
    """

    db_conn, db_cursor = connect()

    query = "DELETE FROM players " \
            "WHERE tournament_id = %s;"

    params = (tournament_id,)

    db_cursor.execute(query, params)
    db_conn.commit()

    _closeDb(db_conn, db_cursor)


def countPlayers(tournament_id=1):
    """Returns the number of players currently registered.

    Args:
        tournament_id: ID of tournament for which players are being counted
    """

    db_conn, db_cursor = connect()

    query = "SELECT COUNT(*) FROM players " \
            "WHERE tournament_id = %s;"

    params = (tournament_id,)

    db_cursor.execute(query, params)
    player_count = db_cursor.fetchone()[0]  # Column 0 contains number of players.

    _closeDb(db_conn, db_cursor)

    return int(player_count)  # Convert to int before returning.


def registerPlayer(name, tournament_id=1):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
      tournament_id: ID of tournament player is registering for
    """

    db_conn, db_cursor = connect()

    query = "INSERT INTO players (name, tournament_id)" \
            "VALUES (%s, %s);"

    paramters = (name, tournament_id)

    db_cursor.execute(query, paramters)
    db_conn.commit()

    _closeDb(db_conn, db_cursor)

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

    db_conn, db_cursor = connect()

    query = "SELECT ps.id, ps.name, ps.wins, ps.matches FROM " \
            "(SELECT * FROM player_standings WHERE tournament_id = %s) ps;"

    params = (tournament_id,)

    db_cursor.execute(query, params)
    results = db_cursor.fetchall()

    _closeDb(db_conn, db_cursor)

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
        db_conn, db_cursor = connect()

        # Select player rows to ensure players are in the correct tournament.
        player_row_query = "SELECT tournament_id " \
                           "FROM players " \
                           "WHERE id = %s OR id = %s;"

        player_row_params = (winner, loser)

        db_cursor.execute(player_row_query, player_row_params)
        player_rows = db_cursor.fetchall()

        # Make sure that winner and loser are not equal, that both players are registered
        # for the correct tournament.
        if winner != loser and (db_cursor.rowcount != 2
                                or player_rows[0][0] != tournament_id
                                or player_rows[1][0] != tournament_id):
            raise TournamentException("Both players must exist and be registered "
                                      "for the correct tournament.")

        # Ensure that players have not already played each other.
        duplicate_match_query = "SELECT count(*) FROM matches " \
                                "WHERE winner_id = %(winner)s AND loser_id = %(loser)s " \
                                "OR winner_id = %(loser)s AND loser_id = %(winner)s;"

        duplicate_match_params = {'winner': winner, 'loser': loser}

        db_cursor.execute(duplicate_match_query, duplicate_match_params)

        if db_cursor.fetchone()[0] != 0:
            raise TournamentException("Players can only have played each other once.")

        insert_query = "INSERT INTO matches (winner_id, loser_id, tournament_id) " \
                       "VALUES (%s, %s, %s);"

        insert_params = (winner, loser, tournament_id)

        db_cursor.execute(insert_query, insert_params)
        db_conn.commit()

        _closeDb(db_conn, db_cursor)


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

    # Player standings are already sorted by wins, so just select pairs
    # from rows returned by playerStandings() function. Player in last place
    # is not paired if number of players is odd.

    return [(standings[i][0], standings[i][1],
             standings[i + 1][0], standings[i + 1][1])
            for i in range(0, len(standings) - 1, 2)]


def _assignBye(tournament_id=1):
    """Assigns a bye on tournaments with odd number of players, increasing
    player's record by 1 win and 1 match. If a tournament has an even number
    of players, the bye is revoked.

    Args:
      tournament_id: tournament ID which bye may be assigned to
    """
    db_conn, db_cursor = connect()

    # If number of players registered for a given tournament is odd, assign
    # a bye. Otherwise, revoke any previously assigned bye by deleting from
    # the assigned_byes table.
    if countPlayers(tournament_id) % 2 != 0:
        # Bye is automatically assigned to the lowest player ID.
        low_player_id_query = "SELECT id FROM players " \
                              "WHERE tournament_id = %s " \
                              "ORDER BY id LIMIT 1;"

        low_player_id_params = (tournament_id,)

        db_cursor.execute(low_player_id_query, low_player_id_params)
        player_id = db_cursor.fetchone()[0]

        insert_query = "INSERT INTO assigned_byes (tournament_id, player_id)" \
                       "VALUES (%s, %s);"

        insert_params = (tournament_id, player_id)

        db_cursor.execute(insert_query, insert_params)
    else:
        delete_query = "DELETE FROM assigned_byes " \
                       "WHERE tournament_id = %s;"

        delete_params = (tournament_id,)

        db_cursor.execute(delete_query, delete_params)

    db_conn.commit()

    _closeDb(db_conn, db_cursor)


def _closeDb(db_conn, db_cursor):
    """Closes database connection and cursor.

    Args:
      db_conn: Database connection object
      db_cursor: Database cursor object
    """

    db_cursor.close()
    db_conn.close()
