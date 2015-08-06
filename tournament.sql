-- Drop database and re-create
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

-- Connect to created database
\c tournament

-- Drop existing tables and views
DROP VIEW player_standings;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS assigned_byes;

-- Players table: tracks only players' names and ID's
CREATE TABLE IF NOT EXISTS players(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	tournament_id INT NOT NULL
);

-- Matches table: tracks winners and losers, along with tournament id
CREATE TABLE IF NOT EXISTS matches(
	winner_id INT REFERENCES players(id) ON DELETE CASCADE,
	loser_id INT REFERENCES players(id) ON DELETE CASCADE,
	tournament_id INT NOT NULL,
	PRIMARY KEY(winner_id, loser_id, tournament_id)
);

-- Assign byes table: tracks which player has been assigned a bye for a given
-- tournament (if any).
CREATE TABLE IF NOT EXISTS assigned_byes(
	tournament_id INT NOT NULL,
	player_id INT REFERENCES players(id) ON DELETE CASCADE,
	PRIMARY KEY(tournament_id, player_id)
);

-- Player standings view: displays table of rows with player ID, player name,
-- wins, and matches columns. Sorted first by number of wins, then OWM (number of wins / number of players).
-- Because players cannot re-play one another, number of opponents equals number of matches.
-- If a player is assigned a bye, their win & match totals are both increased by 1.
CREATE VIEW player_standings AS
	SELECT q.* FROM (SELECT p.*, ((SELECT COUNT(*) FROM matches m WHERE m.winner_id =
	p.id) + (SELECT COUNT(*) FROM assigned_byes b WHERE p.id = b.player_id)) AS wins,
	((SELECT COUNT(*) FROM matches m WHERE m.winner_id = p.id OR m.loser_id = p.id) +
	(SELECT COUNT(*) FROM assigned_byes b WHERE p.id = b.player_id)) AS matches
	FROM players p
	ORDER BY wins DESC) q
	ORDER BY (q.wins / greatest(q.matches, 1)) DESC;