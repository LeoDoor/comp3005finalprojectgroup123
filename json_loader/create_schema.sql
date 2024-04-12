DROP TABLE IF EXISTS fifty_fifty CASCADE;
DROP TABLE IF EXISTS bad_behaviour CASCADE;
DROP TABLE IF EXISTS ball_receipt CASCADE;
DROP TABLE IF EXISTS ball_recovery CASCADE;
DROP TABLE IF EXISTS block CASCADE;
DROP TABLE IF EXISTS carry CASCADE;
DROP TABLE IF EXISTS clearance CASCADE;
DROP TABLE IF EXISTS dribble CASCADE;
DROP TABLE IF EXISTS dribbled_past CASCADE;
DROP TABLE IF EXISTS duel CASCADE;
DROP TABLE IF EXISTS foul_committed CASCADE;
DROP TABLE IF EXISTS foul_won CASCADE;
DROP TABLE IF EXISTS goalkeeper CASCADE;
DROP TABLE IF EXISTS half_end CASCADE;
DROP TABLE IF EXISTS half_start CASCADE;
DROP TABLE IF EXISTS injury_stoppage CASCADE;
DROP TABLE IF EXISTS interception CASCADE;
DROP TABLE IF EXISTS miscontrol CASCADE;
DROP TABLE IF EXISTS pass CASCADE;
DROP TABLE IF EXISTS player_off CASCADE;
DROP TABLE IF EXISTS pressure CASCADE;
DROP TABLE IF EXISTS shot CASCADE;
DROP TABLE IF EXISTS substitution CASCADE;
DROP TABLE IF EXISTS event_relations CASCADE;
DROP TABLE IF EXISTS tactics CASCADE;
DROP TABLE IF EXISTS cards CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS pp_linker CASCADE;
DROP TABLE IF EXISTS outcome CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS play_patterns CASCADE;
DROP TABLE IF EXISTS types CASCADE;
DROP TABLE IF EXISTS shot_types CASCADE;
DROP TABLE IF EXISTS shot_techniques CASCADE;
DROP TABLE IF EXISTS pass_types CASCADE;
DROP TABLE IF EXISTS pass_techniques CASCADE;
DROP TABLE IF EXISTS height CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS managers CASCADE;
DROP TABLE IF EXISTS home_teams CASCADE;
DROP TABLE IF EXISTS away_teams CASCADE;
DROP TABLE IF EXISTS stadiums CASCADE;
DROP TABLE IF EXISTS referee CASCADE;
DROP TABLE IF EXISTS competitions CASCADE;
DROP TABLE IF EXISTS competition_stage CASCADE;
DROP TABLE IF EXISTS seasons CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS body_parts CASCADE;
DROP TABLE IF EXISTS duel_types CASCADE;
DROP TABLE IF EXISTS foul_types CASCADE;
DROP TABLE IF EXISTS keeper_pos CASCADE;
DROP TABLE IF EXISTS keeper_technique CASCADE;
DROP TABLE IF EXISTS keeper_types CASCADE;
DROP TABLE IF EXISTS metadata CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS player_cards CASCADE;
DROP TABLE IF EXISTS carry_event CASCADE;

CREATE TABLE IF NOT EXISTS competitions (
	competition_id INT,
	season_id INT,
	PRIMARY KEY (competition_id, season_id),
	country_name VARCHAR(255),
	competition_name VARCHAR(255),
	competition_gender VARCHAR(50),
	competition_youth BOOLEAN,
	competition_international BOOLEAN,
	season_name VARCHAR(255),
	match_updated VARCHAR(255),
	match_updated_360 VARCHAR(255),
	match_available_360 VARCHAR(255),
	match_available VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS seasons (
	season_id SERIAL UNIQUE PRIMARY KEY,
	season_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS countries (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS managers (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255),
	nickname VARCHAR(255),
	dob VARCHAR(255),
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id)

);


CREATE TABLE IF NOT EXISTS home_teams (
	home_team_id SERIAL UNIQUE PRIMARY KEY,
	home_team_name VARCHAR(255),
	home_team_gender VARCHAR(255),
	home_team_group VARCHAR(255),
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id),
	managers INT,
	FOREIGN KEY (managers) REFERENCES managers(id)
);

CREATE TABLE IF NOT EXISTS away_teams (
	away_team_id SERIAL UNIQUE PRIMARY KEY,
	away_team_name VARCHAR(255),
	away_team_gender VARCHAR(255),
	away_team_group VARCHAR(255),
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id),
	managers INT,
	FOREIGN KEY (managers) REFERENCES managers(id)
);

CREATE TABLE IF NOT EXISTS metadata (
	metadata_id SERIAL UNIQUE PRIMARY KEY,
	data_version VARCHAR(255),
	shot_fidelity_version VARCHAR(255),
	xy_fidelity_version VARCHAR(255)
	
);

CREATE TABLE IF NOT EXISTS competition_stage (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stadiums (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255),
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id)
);

CREATE TABLE IF NOT EXISTS referee (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255),
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id)
);

CREATE TABLE IF NOT EXISTS matches (
	match_id SERIAL UNIQUE PRIMARY KEY,
	match_date VARCHAR(255),
	kick_off VARCHAR(255),
	competition INT,
	season INT,
	FOREIGN KEY (competition, season) REFERENCES competitions(competition_id, season_id),
	home_team INT,
	FOREIGN KEY (home_team) REFERENCES home_teams(home_team_id),
	away_team INT,
	FOREIGN KEY (away_team) REFERENCES away_teams(away_team_id),
	home_score INT,
	away_score INT,
	match_status VARCHAR(255),
	match_status_360 VARCHAR(255),
	last_updated VARCHAR(255),
	last_updated_360 VARCHAR(255),
	metadata INT,
	FOREIGN KEY (metadata) REFERENCES metadata(metadata_id),
	match_week INT,
	competition_stage INT,
	FOREIGN KEY (competition_stage) REFERENCES competition_stage(id),
	stadium INT,
	FOREIGN KEY (stadium) REFERENCES stadiums(id)

);

CREATE TABLE IF NOT EXISTS teams (
	team_id SERIAL UNIQUE PRIMARY KEY,
	team_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS players (
	player_id SERIAL UNIQUE PRIMARY KEY,
	team INT,
	FOREIGN KEY (team) REFERENCES teams(team_id),
	player_name VARCHAR(255),
	player_nickname VARCHAR(255),
	jersey_number INT,
	country INT,
	FOREIGN KEY (country) REFERENCES countries(id)
	
);

CREATE TABLE IF NOT EXISTS positions (
	position_id SERIAL UNIQUE PRIMARY KEY,
	position_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS pp_linker (
	pp_id SERIAL UNIQUE PRIMARY KEY,
	player_id INT,
	FOREIGN KEY (player_id) REFERENCES players(player_id),
	position_id INT,
	FOREIGN KEY (position_id) REFERENCES positions(position_id),
	from_time VARCHAR(255),
	to_time VARCHAR(255),
	from_period INT,
	to_period INT,
	start_reason VARCHAR(255),
	end_reason VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS player_cards (
	card_id SERIAL UNIQUE PRIMARY KEY,
	player INT,
	FOREIGN KEY (player) REFERENCES players(player_id),
	time VARCHAR(255),
	card_type VARCHAR(255),
	reason VARCHAR(255),
	period INT
);



CREATE TABLE IF NOT EXISTS types (
	type_id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS play_patterns (
	pp_id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS events (
	event_id VARCHAR(255) UNIQUE PRIMARY KEY,
	match_id INT,
	FOREIGN KEY (match_id) REFERENCES matches(match_id),
	event_index INT,
	event_period INT,
	timestamp VARCHAR(255),
	minute INT,
	second INT,
	type INT,
	FOREIGN KEY (type) REFERENCES types(type_id),
	possession INT,
	possession_team INT,
	FOREIGN KEY (possession_team) REFERENCES teams(team_id),
	play_pattern INT,
	FOREIGN KEY (play_pattern) REFERENCES play_patterns(pp_id),
	team INT,
	FOREIGN KEY (team) REFERENCES teams(team_id),
	player INT,
	FOREIGN KEY (player) REFERENCES players(player_id),
	position INT,
	FOREIGN KEY (position) REFERENCES positions(position_id),
	loc_x FLOAT,
	loc_y FLOAT,
	duration FLOAT,
	under_pressure BOOLEAN,
	off_camera BOOLEAN,
	ball_out BOOLEAN
	
);

CREATE TABLE IF NOT EXISTS carry (
	carry_id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	end_loc_x FLOAT,
	end_loc_y FLOAT
);

CREATE TABLE IF NOT EXISTS event_relations (
	event_id VARCHAR(255),
	related_to VARCHAR(255),
	PRIMARY KEY (event_id, related_to),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	FOREIGN KEY (related_to) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS tactics (
	tactic_id VARCHAR(255) UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	formation INT,
	player_1 INT,
	pos_1 INT,
	player_2 INT,
	pos_2 INT,
	player_3 INT,
	pos_3 INT,
	player_4 INT,
	pos_4 INT,
	player_5 INT,
	pos_5 INT,
	player_6 INT,
	pos_6 INT,
	player_7 INT,
	pos_7 INT,
	player_8 INT,
	pos_8 INT,
	player_9 INT,
	pos_9 INT,
	player_10 INT,
	pos_10 INT,
	player_11 INT,
	pos_11 INT,
	FOREIGN KEY (player_1) REFERENCES players(player_id),
	FOREIGN KEY (pos_1) REFERENCES positions(position_id)
);

CREATE TABLE IF NOT EXISTS outcome (
	outcome_id SERIAL UNIQUE PRIMARY KEY,
	outcome_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cards (
	card_id SERIAL UNIQUE PRIMARY KEY,
	card_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS body_parts (
	bp_id SERIAL UNIQUE PRIMARY KEY,
	bp_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS duel_types (
	type_id SERIAL UNIQUE PRIMARY KEY,
	type_name VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS foul_types (
	type_id SERIAL UNIQUE PRIMARY KEY,
	type_name VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS keeper_pos (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS keeper_technique (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS keeper_types (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS height (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS pass_types (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS pass_techniques (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS shot_techniques (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS shot_types (
	id SERIAL UNIQUE PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS fifty_fifty (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	outcome_id INT,
	FOREIGN KEY (outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE IF NOT EXISTS bad_behaviour (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	card_id INT,
	FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

CREATE TABLE IF NOT EXISTS ball_receipt (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	outcome_id INT,
	FOREIGN KEY (outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE IF NOT EXISTS ball_recovery (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	offensive BOOLEAN DEFAULT FALSE,
	recovery_failure BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS block (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	deflection BOOLEAN DEFAULT FALSE,
	offensive BOOLEAN DEFAULT FALSE,
	save_block BOOLEAN DEFAULT FALSE,
	counterpress BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS carry_event (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	end_x FLOAT,
	end_y FLOAT
);

CREATE TABLE IF NOT EXISTS clearance (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	aerial_won BOOLEAN,
	body_part INT,
	FOREIGN KEY (body_part) REFERENCES body_parts(bp_id)
);

CREATE TABLE IF NOT EXISTS dribble(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	overrun BOOLEAN,
	nutmeg BOOLEAN,
	outcome_id INT,
	FOREIGN KEY (outcome_id) REFERENCES outcome(outcome_id),
	no_touch BOOLEAN
);

CREATE TABLE IF NOT EXISTS dribbled_past (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	counterpress BOOLEAN
);

CREATE TABLE IF NOT EXISTS duel (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	counterpress BOOLEAN DEFAULT FALSE,
	duel_type INT,
	FOREIGN KEY (duel_type) REFERENCES duel_types(type_id),
	outcome_id INT,
	FOREIGN KEY (outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE IF NOT EXISTS foul_committed(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	counterpress BOOLEAN,
	offensive BOOLEAN,
	foul_type INT,
	FOREIGN KEY (foul_type) REFERENCES foul_types(type_id),
	advantage BOOLEAN,
	penalty BOOLEAN,
	card_id INT,
	FOREIGN KEY (card_id) REFERENCES cards(card_id)
);


CREATE TABLE IF NOT EXISTS foul_won (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	defensive BOOLEAN,
	advantage BOOLEAN,
	penalty BOOLEAN
);

CREATE TABLE IF NOT EXISTS goalkeeper(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	keeper_pos INT,
	FOREIGN KEY (keeper_pos) REFERENCES keeper_pos(id),
	keeper_technique INT,
	FOREIGN KEY (keeper_technique) REFERENCES keeper_technique(id),
	body_part INT,
	FOREIGN KEY (body_part) REFERENCES body_parts(bp_id),
	keeper_type INT,
	FOREIGN KEY (keeper_type) REFERENCES keeper_types(id),
	outcome INT,
	FOREIGN KEY (outcome) REFERENCES outcome(outcome_id)
);


CREATE TABLE IF NOT EXISTS half_end (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	early_video_end BOOLEAN,
	match_suspended BOOLEAN
);

CREATE TABLE IF NOT EXISTS half_start (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	late_video_start BOOLEAN
);

CREATE TABLE IF NOT EXISTS injury_stoppage (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	in_chain BOOLEAN
);

CREATE TABLE IF NOT EXISTS interception (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	outcome INT,
	FOREIGN KEY (outcome) REFERENCES outcome(outcome_id)
);

CREATE TABLE IF NOT EXISTS miscontrol (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	aerial_won BOOLEAN
);

CREATE TABLE IF NOT EXISTS pass(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	recipient INT,
	FOREIGN KEY (recipient) REFERENCES players(player_id),
	length FLOAT,
	angle FLOAT,
	height INT,
	FOREIGN KEY (height) REFERENCES height(id),
	end_loc_x FLOAT,
	end_loc_y FLOAT,
	assisted_shot_id VARCHAR(225),
	FOREIGN KEY (assisted_shot_id) REFERENCES events(event_id),
	backheel BOOLEAN,
	deflected BOOLEAN,
	miscommunication BOOLEAN,
	cross_pass BOOLEAN,
	cut_back BOOLEAN,
	switch BOOLEAN,
	shot_assist BOOLEAN,
	goal_assist BOOLEAN,
	body_part INT,
	FOREIGN KEY (body_part) REFERENCES body_parts(bp_id),
	pass_type INT,
	FOREIGN KEY (pass_type) REFERENCES pass_types(id),
	outcome INT,
	FOREIGN KEY (outcome) REFERENCES outcome(outcome_id),
	technique INT,
	FOREIGN KEY (technique) REFERENCES pass_techniques(id)
);

CREATE TABLE IF NOT EXISTS player_off(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	permanent BOOLEAN
);

CREATE TABLE IF NOT EXISTS pressure(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	counterpress BOOLEAN
);

CREATE TABLE IF NOT EXISTS shot(
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	key_pass_id VARCHAR(255),
	FOREIGN KEY(key_pass_id) REFERENCES events(event_id),
	end_loc_x FLOAT,
	end_loc_y FLOAT,
	end_loc_z FLOAT,
	aerial_won BOOLEAN DEFAULT False,
	follows_dribble BOOLEAN,
	first_time BOOLEAN,
	freeze_frame JSONB ARRAY,
	open_goal BOOLEAN,
	statsbomb_xg NUMERIC,
	deflected BOOLEAN,
	shot_technique INT,
	FOREIGN KEY (shot_technique) REFERENCES shot_techniques(id),
	body_part INT,
	FOREIGN KEY (body_part) REFERENCES body_parts(bp_id),
	shot_type INT,
	FOREIGN KEY (shot_type) REFERENCES shot_types(id),
	outcome INT,
	FOREIGN KEY (outcome) REFERENCES outcome(outcome_id)
);


CREATE TABLE IF NOT EXISTS substitution (
	id SERIAL UNIQUE PRIMARY KEY,
	event_id VARCHAR(255),
	FOREIGN KEY (event_id) REFERENCES events(event_id),
	replacement INT,
	FOREIGN KEY (replacement) REFERENCES players(player_id),
	outcome INT,
	FOREIGN KEY (outcome) REFERENCES outcome(outcome_id)
);

