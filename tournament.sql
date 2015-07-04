-- Connect tournament database
\c tournament

-- Drop existing tables and views
drop view player_standings;
drop table if exists matches;
drop table if exists players;
drop table if exists assigned_byes;

-- Players table: tracks only players' names and ID's
create table if not exists players(
	id serial primary key,
	name text not null,
	tournament_id int
);

-- Matches table: tracks winners and losers, along with tournament id
create table if not exists matches(
	winner_id int,
	loser_id int,
	tournament_id int,
	primary key(winner_id, loser_id, tournament_id)
);

-- Assign byes table: tracks which player has been assigned a bye for a given
-- tournament (if any).
create table if not exists assigned_byes(
	tournament_id int,
	player_id int,
	primary key(tournament_id, player_id)
);

-- Player standings view: displays table of rows with player ID, player name,
-- wins, and matches columns. Sorted first by number of wins, then OWM (number of wins / number of players).
-- Because players cannot re-play one another, number of opponents equals number of matches.
-- If a player is assigned a bye, their win & match totals are both increased by 1.
create view player_standings as
	select q.* from (select p.*, ((select count(*) from matches m where m.winner_id =
	p.id) + (select count(*) from assigned_byes b where p.id = b.player_id)) as wins,
	((select count(*) from matches m where m.winner_id = p.id or m.loser_id = p.id) +
	(select count(*) from assigned_byes b where p.id = b.player_id)) as matches
	from players p
	order by wins) q
	order by q.wins / greatest(q.matches, 1);