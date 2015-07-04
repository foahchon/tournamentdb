#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *
from tournament_exception import TournamentException


def testDeleteMatches():
    deleteMatches(1)
    deleteMatches(2)
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches(1)
    deleteMatches(2)
    deletePlayers(1)
    deletePlayers(2)
    print "2. Player records can be deleted."


def testCount():
    deleteMatches(1)
    deleteMatches(2)
    deletePlayers(1)
    deletePlayers(2)
    c1 = countPlayers(1)
    c2 = countPlayers(2)
    if c1 == '0' or c2 == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c1 != 0 or c2 != 0:
        raise ValueError("After deleting, countPlayers should return zero for both tournaments.")
    print "3. After deleting, countPlayers() returns zero for multiple tournaments."


def testRegister():
    deleteMatches(1)
    deleteMatches(2)
    deletePlayers(1)
    deletePlayers(2)
    registerPlayer("Chandra Nalaar")
    registerPlayer("B.J. Blazkowitz", 2)
    c1 = countPlayers(1)
    c2 = countPlayers(2)
    if c1 != 1 or c2 != 1:
        raise ValueError(
            "After one player registers for two tournaments, countPlayers() should be 1 for multiple tournaments.")
    print "4. After registering one player each to two tournaments, countPlayers() returns 1 for multiple tournaments."


def testRegisterCountDelete():
    deleteMatches(1)
    deleteMatches(2)
    deletePlayers(1)
    deletePlayers(2)
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi", 2)
    registerPlayer("Atlanta Hope", 2)
    c1 = countPlayers(1)
    c2 = countPlayers(2)
    if c1 != 2 or c2 != 2:
        raise ValueError(
            "After registering four players, countPlayers should be 2 for each tournament.")
    deletePlayers(1)
    deletePlayers(2)
    c1 = countPlayers()
    c2 = countPlayers(2)
    if c1 != 0 or c2 != 0:
        raise ValueError("After deleting, countPlayers should return zero for both tournaments.")
    print "5. Players can be registered and deleted for both tournaments."


def testStandingsBeforeMatches():
    deleteMatches(1)
    deleteMatches(2)
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    registerPlayer("B.J. Blazkowitz", 2)
    registerPlayer("Flynn Taggart", 2)
    standings = playerStandings()
    standings2 = playerStandings(2)
    if len(standings) < 2 or len(standings2) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2 or len(standings2) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4 or len(standings2[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")

    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")

    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings2
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins (2).")
    if set([name1, name2]) != set(["B.J. Blazkowitz", "Flynn Taggart"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played (2).")

    print "6. Newly registered players appear in the standings with no matches in both tournaments."


def testReportMatches():
    deleteMatches(1)
    deleteMatches(2)
    deletePlayers(1)
    deletePlayers(2)
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    registerPlayer("B.J. Blazkowitz", 2)
    registerPlayer("Flynn Taggart", 2)

    standings = playerStandings()
    standings2 = playerStandings(2)

    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4, 1)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")

    [id1, id2] = [row[0] for row in standings2]
    reportMatch(id1, id2, 2)
    standings2 = playerStandings(2)
    for (i, n, w, m) in standings2:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i == id1 and w != 1:
            raise ValueError("Each match winner should have one win recorded.")

    print "7. After a match, players have updated standings for both tournaments."


def testPairings():
    deleteMatches(1)
    deletePlayers(1)
    deletePlayers(2)
    deleteMatches(2)
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("B.J. Blackowicz", 2)
    registerPlayer("Flynn Taggart", 2)
    registerPlayer("Commander Keen", 2)
    registerPlayer("Dangerous Dave", 2)

    standings = playerStandings(1)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4, 1)
    pairings = swissPairings(1)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")

    standings2 = playerStandings(2)
    [id1, id2, id3, id4] = [row[0] for row in standings2]
    reportMatch(id1, id2, 2)
    reportMatch(id3, id4, 2)
    pairings = swissPairings(2)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")

    print "8. After one match, players with one win are paired for both tournaments."


def testByes():
    deletePlayers(1)
    deletePlayers(2)
    deleteMatches(1)
    deleteMatches(2)

    registerPlayer("Flynn Taggart", 1)

    standings = playerStandings(1)

    (wins, matches) = standings[0][2:]

    if wins != 1 or matches != 1:
        raise ValueError(
            "After one player registers, player should have record of 1 win, 1 match due to bye."
        )
    registerPlayer("B.J. Blackowicz", 1)

    standings = playerStandings(1)
    records = [(x[2:]) for x in standings]

    if records[0][0] != 0 or records[0][1] != 0 \
            or records[1][0] != 0 or records[1][1] != 0:
        raise ValueError(
            "After two players register, wins and losses should be zero for both players."
        )

    print "9. After one match, players with assigned bye have 1 win and 1 match."


def testNoRepeatMatches():
    deletePlayers(1)
    deletePlayers(2)
    deleteMatches(1)
    deleteMatches(2)

    registerPlayer("Flynn Taggart", 1)
    registerPlayer("B.J. Blackowicz", 1)

    [id1, id2] = [row[0] for row in playerStandings()]

    try:
        reportMatch(id1, id2, 1)
        reportMatch(id2, id1, 1)
    except TournamentException:
        print "10. Players cannot play each other more than once."
        return
    else:
        raise ValueError(
            "Players should not be able to play each other more than once."
        )


def testDrawDoesNotAffectStandings():
    deletePlayers(1)
    deletePlayers(2)
    deleteMatches(1)
    deleteMatches(2)

    registerPlayer("Flynn Taggart", 1)
    registerPlayer("B.J. Blackowicz", 1)

    oldStandings = playerStandings(1)
    [id1, id2] = [row[0] for row in oldStandings]

    reportMatch(id1, id2, 1, True)

    newStandings = playerStandings(1)

    if oldStandings != newStandings:
        raise ValueError(
            "Reporting draw should not affect standings."
        )

    print "11. Reporting a draw does not affect standings."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testByes()
    testNoRepeatMatches()
    testDrawDoesNotAffectStandings()

    print "Success!  All tests pass!"
