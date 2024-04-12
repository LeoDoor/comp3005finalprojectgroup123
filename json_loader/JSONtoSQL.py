
import psycopg
import json
import os

# pg_dump -h localhost -U postgres -d project_database -f dbexport.sql

custom_password = "SQLAndy!"
data_loc = r"C:\Users\mattv\Git\open-data\data"
# data_loc = r"C:\Users\mattv\OneDrive - Carleton University\Documents\GitHub\open-data\data"
match_list = [[2,44],[11,4],[11,42],[11,90]] # [competition_id, season_id]
# match_list = [[2,44]]
match_ids = []
dir_path = os.path.dirname(os.path.realpath(__file__))

conn = psycopg.connect(
	dbname="project_database",
	user="postgres",
	password=custom_password,
	host="localhost"
)

# Create a cursor object using the connection
cur = conn.cursor()

# schema = open(os.path.join(dir_path, "create_schema.sql"), 'r').read()
# dbexport = open(os.path.join(dir_path, "dbexport.sql"), 'w', encoding='utf-8')


seasons_list = []
countries_list = []
competition_stage_list = []
stadiums_list = []
managers_list = []


# Open the JSON file
with open(fr"{data_loc}\competitions.json", encoding='utf-8') as file:
	data = json.load(file)

# Iterate over the JSON data and insert into the table
pk = 1
for entry in data:
	cur.execute("""
	    INSERT INTO competitions (
			competition_id,
			season_id,
			country_name,
			competition_name,
			competition_gender,
			competition_youth,
			competition_international,
			season_name,
			match_updated,
			match_updated_360,
			match_available_360,
			match_available
		) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		ON CONFLICT DO NOTHING;
	""" , (
		entry['competition_id'],
		entry['season_id'],
		entry['country_name'],
		entry['competition_name'],
		entry['competition_gender'],
		entry['competition_youth'],
		entry['competition_international'],
		entry['season_name'],
		entry['match_updated'],
		entry['match_updated_360'],
		entry['match_available_360'],
		entry['match_available'],
	))
	pk += 1

conn.commit()


for match in match_list:
	print(f"========={match[1]}.json=========")
	with open(fr"{data_loc}\matches\{match[0]}\{match[1]}.json", encoding='utf-8') as file:
		data = json.load(file)

	# Iterate over the JSON data and insert into the table
	for entry in data:
		print(f"attempting entry on match_id: {entry['match_id']}")
		match_ids.append(entry['match_id'])

		print(f"\tinserting seasons")
		if entry['season']['season_id'] not in seasons_list:
			cur.execute("""
				INSERT INTO seasons (
					season_id,
					season_name
				) VALUES (%s, %s)
				ON CONFLICT DO NOTHING;
			""", (
				entry['season']['season_id'],
				entry['season']['season_name']
			))
			seasons_list.append(entry['season']['season_id'])

		print(f"\tinserting countries")
		if entry['home_team']['country']['id'] not in countries_list or entry['away_team']['country']['id'] not in countries_list:
			cur.execute("""
				INSERT INTO countries (
					id,
					name
				) VALUES (%s, %s),(%s, %s)
				ON CONFLICT DO NOTHING;
			""" , (
				entry['home_team']['country']['id'],
				entry['home_team']['country']['name'],
				entry['away_team']['country']['id'],
				entry['away_team']['country']['name']
			))
			if entry['home_team']['country']['id'] not in countries_list:
				countries_list.append(entry['home_team']['country']['id'])
			if entry['away_team']['country']['id'] not in countries_list:
				countries_list.append(entry['away_team']['country']['id'])

		if entry['home_team'].get('managers', []):
			for manager in entry['home_team']['managers']:
				if manager['country']['id'] not in countries_list:
					cur.execute("""
						INSERT INTO countries (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;
					""" , (
						manager['country']['id'],
						manager['country']['name']
					))
					countries_list.append(manager['country']['id'])
		if entry['away_team'].get('managers', []):
			for manager in entry['away_team']['managers']:
				if manager['country']['id'] not in countries_list:
					cur.execute("""
						INSERT INTO countries (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;
					""" , (
						manager['country']['id'],
						manager['country']['name']
					))
					countries_list.append(manager['country']['id'])

		print(f"\tinserting metadata")
		cur.execute("""
			INSERT INTO metadata (
				metadata_id,
				data_version,
				shot_fidelity_version,
				xy_fidelity_version
			) VALUES (%s, %s, %s, %s)
			ON CONFLICT DO NOTHING;
		""" , (
			entry['match_id'],
			entry['metadata']['data_version'],
			entry['metadata']['shot_fidelity_version'],
			entry['metadata']['xy_fidelity_version'] if entry['metadata'].get('xy_fidelity_version',[]) else None
		))

		print(f"\tinserting competition_stage")
		if entry['competition_stage']['id'] not in competition_stage_list:
			cur.execute("""
				INSERT INTO competition_stage (
					id,
					name
				) VALUES (%s, %s)
				ON CONFLICT DO NOTHING;
			""" , (
				entry['competition_stage']['id'],
				entry['competition_stage']['name']
			))
			competition_stage_list.append(entry['competition_stage']['id'])

		print(f"\tinserting stadiums")
		if entry.get('stadium',[]):
			if entry['stadium']['id'] not in stadiums_list:
				cur.execute("""
					INSERT INTO stadiums (
						id,
						name,
						country
					) VALUES (%s, %s, %s)
					ON CONFLICT DO NOTHING;
				""" , (
					entry['stadium']['id'],
					entry['stadium']['name'],
					entry['stadium']['country']['id']
				))
				stadiums_list.append(entry['stadium']['id'])

		print(f"\tinserting managers")
		if entry['away_team'].get('managers', []):
			for manager in entry['away_team']['managers']:
				if manager['id'] not in managers_list:
					cur.execute("""
						INSERT INTO managers (
							id,
							name,
							nickname,
							dob,
							country
						) VALUES (%s, %s, %s, %s, %s)
						ON CONFLICT DO NOTHING;
					""" , (
						manager['id'],
						manager['name'],
						manager['nickname'],
						manager['dob'],
						manager['country']['id']
					))
					managers_list.append(manager['id'])

		if entry['home_team'].get('managers', []):
			for manager in entry['home_team']['managers']:
				if manager['id'] not in managers_list:
					cur.execute("""
						INSERT INTO managers (
							id,
							name,
							nickname,
							dob,
							country
						) VALUES (%s, %s, %s, %s, %s)
						ON CONFLICT DO NOTHING;
					""" , (
						manager['id'],
						manager['name'],
						manager['nickname'],
						manager['dob'],
						manager['country']['id']
					))
					managers_list.append(manager['id'])

		print(f"\tinserting home_teams")
		cur.execute("""
			INSERT INTO home_teams (
				home_team_id,
				home_team_name,
				home_team_gender,
				home_team_group,
				country,
				managers
			) VALUES (%s, %s, %s, %s, %s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['home_team']['home_team_id'],
			entry['home_team']['home_team_name'],
			entry['home_team']['home_team_gender'],
			entry['home_team']['home_team_group'] if entry['home_team'].get('home_team_group',()) else None,
			entry['home_team']['country']['id'],
			entry['home_team']['managers'][0]['id'] if entry['home_team'].get('managers', []) else None
		))

		print(f"\tinserting away_teams")
		cur.execute("""
			INSERT INTO away_teams (
				away_team_id,
				away_team_name,
				away_team_gender,
				away_team_group,
				country,
				managers
			) VALUES (%s, %s, %s, %s, %s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['away_team']['away_team_id'],
			entry['away_team']['away_team_name'],
			entry['away_team']['away_team_gender'],
			entry['away_team']['away_team_group'] if entry['away_team'].get('away_team_group',()) else None,
			entry['away_team']['country']['id'],
			entry['away_team']['managers'][0]['id'] if entry['away_team'].get('managers', []) else None
		))

		print(f"\tinserting matches")
		cur.execute("""
			INSERT INTO matches (
				match_id,
				match_date,
				kick_off,
				competition,
				season,
				home_team,
				away_team,
				home_score,
				away_score,
				match_status,
				match_status_360,
				last_updated,
				last_updated_360,
				metadata,
				match_week,
				competition_stage,
				stadium
			) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['match_id'],
			entry['match_date'],
			entry['kick_off'],
			entry['competition']['competition_id'],
			entry['season']['season_id'],
			entry['home_team']['home_team_id'],
			entry['away_team']['away_team_id'],
			entry['home_score'],
			entry['away_score'],
			entry['match_status'],
			entry['match_status_360'],
			entry['last_updated'],
			entry['last_updated_360'],
			entry['match_id'],
			entry['match_week'],
			entry['competition_stage']['id'],
			entry['stadium']['id'] if entry.get("stadium",()) else None
		))

for id in match_ids:
	print(fr"=========lineups\{id}.json=========")
	with open(fr"{data_loc}\lineups\{id}.json", encoding='utf-8') as file:
		data = json.load(file)

	# Iterate over the JSON data and insert into the table
	for entry in data:
		print(f"attempting entry on team_id: {entry['team_id']}")
		cur.execute("""
			INSERT INTO teams (
				team_id,
				team_name
			) VALUES (%s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['team_id'],
			entry['team_name']
		))



		for player in entry['lineup']:
			cur.execute("""
				INSERT INTO countries (
					id,
					name
				) VALUES (%s, %s)
				ON CONFLICT DO NOTHING;		
			""" , (
				player['country']['id'],
				player['country']['name']
			))

			cur.execute("""
				INSERT INTO players (
					player_id,
					team,
					player_name,
					player_nickname,
					jersey_number,
					country
				) VALUES (%s, %s, %s, %s, %s, %s)
				ON CONFLICT DO NOTHING;		
			""" , (
				player['player_id'],
				entry['team_id'],
				player['player_name'],
				player['player_nickname'] if player.get('player_nickname', ()) else None,
				player['jersey_number'],
				player['country']['id']
			))
			for card in player['cards']:
				cur.execute("""
					INSERT INTO player_cards (
						player,
						time,
						card_type,
						reason,
						period
					) VALUES (%s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					player["player_id"],
					card['time'],
					card['card_type'],
					card['reason'],
					card['period']
				))



			for position in player['positions']:
				cur.execute("""
					INSERT INTO positions (
						position_id,
						position_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					position['position_id'],
					position['position']
					))

				cur.execute("""
					INSERT INTO pp_linker (
						player_id,
						position_id,
						from_time,
						to_time,
						from_period,
						to_period,
						start_reason,
						end_reason
					) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					player['player_id'],
					position['position_id'],
					position['from'],
					position['to'] if position.get('to', ()) else None,
					position['from_period'],
					position['to_period'] if position.get('to_period', ()) else None,
					position["start_reason"],
					position["end_reason"]
				))

event_num = 0
for id in match_ids:
	event_num += 1
	print(fr"events\{id}.json Wrapper  ({event_num}/{len(match_ids)})")

	with open(fr"{data_loc}\events\{id}.json", encoding='utf-8') as file:
		data = json.load(file)

	# Iterate over the JSON data and insert into the table
	for entry in data:
		cur.execute("""
			INSERT INTO play_patterns (
				pp_id,
				name
			) VALUES (%s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['play_pattern']['id'],
			entry['play_pattern']['name']
		))

		cur.execute("""
			INSERT INTO types (
				type_id,
				name
			) VALUES (%s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['type']['id'],
			entry['type']['name']
		))
		if entry.get('position'):
			cur.execute("""
				INSERT INTO positions (
					position_id,
					position_name
				) VALUES (%s, %s)
				ON CONFLICT DO NOTHING;		
			""" , (
				entry['position']['id'],
				entry['position']['name']
			))

		# if entry['type']['id'] == 27 and (entry.get('player_off') or entry.get('permanent')):

		# 	print(f"PLAYER OFF IN {id}.json")
		# 	input()
			

		cur.execute("""
			INSERT INTO events (
				event_id,
			  	match_id,
				event_index,
				event_period,
				timestamp,
				minute,
				second,
				type,
				possession,
				possession_team,
				play_pattern,
				team,
				player,
				position,
				loc_x,
				loc_y,
				duration,
				under_pressure,
				off_camera,
				ball_out
			) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT DO NOTHING;		
		""" , (
			entry['id'],
			id,
			entry['index'],
			entry['period'],
			entry['timestamp'],
			entry['minute'],
			entry['second'],
			entry['type']['id'],
			entry['possession'],
			entry['possession_team']['id'],
			entry['play_pattern']['id'],
			entry['team']['id'],
			entry['player']['id'] if entry.get('player', ()) else None,
			entry['position']['id'] if entry.get('position', ()) else None,
			entry['location'][0] if entry.get('location',()) else None,
			entry['location'][1] if entry.get('location',()) else None,
			entry['duration'] if entry.get('duration', ()) else None,
			entry['under_pressure'] if entry.get('under_pressure', ()) else None,
			entry['off_camera'] if entry.get('off_camera', ()) else None,
			entry['ball_out'] if entry.get('ball_out', ()) else None

		))


event_num = 0
for id in match_ids:
	event_num += 1
	print(fr"events\{id}.json Cases  ({event_num}/{len(match_ids)})")

	with open(fr"{data_loc}\events\{id}.json", encoding='utf-8') as file:
		data = json.load(file)

	for entry in data:
		match entry['type']['id']:
			case 2: #Ball Recovery
				if entry.get('ball_recovery',()):
					cur.execute("""
						INSERT INTO ball_recovery (
							event_id,
							offensive,
							recovery_failure
						) VALUES (%s, %s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['ball_recovery']['offensive'] if entry['ball_recovery'].get('offensive',()) else False,
						entry['ball_recovery']['recovery_failure'] if entry['ball_recovery'].get('recovery_failure',()) else False
					))
				else:
					cur.execute("""
						INSERT INTO ball_recovery (
							event_id,
				 			offensive,
							recovery_failure
						) VALUES (%s, %s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						False,
						False
					))
			case 3: # Dispossessed
				pass
			case 4: # Duel
				if entry['duel'].get('outcome',()):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['duel']['outcome']['id'],
						entry['duel']['outcome']['name']
					))
				
				cur.execute("""
					INSERT INTO duel_types (
						type_id,
						type_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['duel']['type']['id'],
					entry['duel']['type']['name']
				))

				cur.execute("""
					INSERT INTO duel (
						event_id,
						counterpress,
						duel_type,
						outcome_id
					) VALUES (%s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['counterpress'] if entry.get('counterpress',()) else False,
					entry['duel']['type']['id'],
					entry['duel']['outcome']['id'] if entry['duel'].get('outcome',()) else None
				))

			case 6: # Block
				if entry.get('block',()):
					cur.execute("""
					INSERT INTO block (
						event_id,
						deflection,
				 		offensive,
						save_block,
						counterpress
					) VALUES (%s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['block']['deflection'] if entry['block'].get('deflection',()) else False,
						entry['block']['offensive'] if entry['block'].get('offensive',()) else False,
						entry['block']['save_block'] if entry['block'].get('save_block',()) else False,
						entry['counterpress'] if entry.get("counterpess") else False
					))
				elif entry.get('counterpress'):
					cur.execute("""
					INSERT INTO block (
						event_id,
						counterpress
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['counterpress'] if entry.get("counterpess") else False
					))
			case 8:	# Offside
				pass
			case 9: # Clearance
				cur.execute("""
					INSERT INTO body_parts (
						bp_id,
						bp_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['clearance']['body_part']['id'],
					entry['clearance']['body_part']['name']
				))

				cur.execute("""
					INSERT INTO clearance (
						event_id,
						aerial_won,
						body_part
					) VALUES (%s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['clearance']['aerial_won'] if entry['clearance'].get('aerial_won',()) else False,
					entry['clearance']['body_part']['id']
				))
			case 10: # Interception
				if entry['interception'].get('outcome',()):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['interception']['outcome']['id'],
						entry['interception']['outcome']['name']
					))

					cur.execute("""
						INSERT INTO interception (
							event_id,
							outcome
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['interception']['outcome']['id']
					))
				else:
					print("NO INTERCEPTION FOR INTERCEPTION TYPE???")

			case 14: # Dribble
				if entry['dribble'].get('outcome',()):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['dribble']['outcome']['id'],
						entry['dribble']['outcome']['name']
					))

					cur.execute("""
						INSERT INTO dribble (
							event_id,
				 			overrun,
				 			nutmeg,
							outcome_id,
							no_touch
						) VALUES (%s, %s, %s, %s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['dribble']['overrun'] if entry['dribble'].get('overrun') else False,
						entry['dribble']['nutmeg'] if entry['dribble'].get('nutmeg') else False,
						entry['dribble']['outcome']['id'],
						entry['dribble']['no_touch'] if entry['dribble'].get('no_touch') else False
					))

			case 16: # Shot
				cur.execute("""
					INSERT INTO shot_techniques (
						id,
						name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['shot']['technique']['id'],
					entry['shot']['technique']['name']
				))

				cur.execute("""
					INSERT INTO body_parts (
						bp_id,
						bp_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['shot']['body_part']['id'],
					entry['shot']['body_part']['name']
				))

				cur.execute("""
					INSERT INTO shot_types (
						id,
						name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['shot']['type']['id'],
					entry['shot']['type']['name']
				))

				cur.execute("""
					INSERT INTO outcome (
						outcome_id,
						outcome_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['shot']['outcome']['id'],
					entry['shot']['outcome']['name']
				))

				cur.execute("""
					INSERT INTO shot (
						event_id,
						key_pass_id,
						end_loc_x,
						end_loc_y,
						end_loc_z,
						aerial_won,
						follows_dribble,
						first_time,
						freeze_frame,
						open_goal,
						statsbomb_xg,
						deflected,
						shot_technique,
						body_part,
						shot_type,
						outcome
					) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['shot']['key_pass_id'] if entry['shot'].get('key_pass_id') else None,
					entry['shot']['end_location'][0],
					entry['shot']['end_location'][1],
					entry['shot']['end_location'][2] if len(entry['shot']['end_location']) == 3 else None,
					entry['shot']['aerial_won'] if entry['shot'].get('aerial_won') else False,
					entry['shot']['follows_dribble'] if entry['shot'].get('follows_dribble') else False,
					entry['shot']['first_time'] if entry['shot'].get('first_time') else False,
					None,
					entry['shot']['open_goal'] if entry['shot'].get('open_goal') else False,
					entry['shot']['statsbomb_xg'],
					entry['shot']['deflected'] if entry['shot'].get('deflected') else False,
					entry['shot']['technique']['id'],
					entry['shot']['body_part']['id'],
					entry['shot']['type']['id'],
					entry['shot']['outcome']['id']
				))

			case 17: # Pressure
				cur.execute("""
                    INSERT INTO pressure (
                        event_id,
                        counterpress
                    ) VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    entry['id'],
                    entry['counterpress'] if entry.get('counterpress') else False 
                ))
                            
			case 18: # Half Start
				cur.execute("""
                    INSERT INTO half_start (
                        event_id,
                        late_video_start
                    ) VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    entry['id'],
                    entry['half_start']['late_video_start'] if entry.get('half_start') and entry['half_start'].get('late_video_start') else False
                ))
                
			case 19: # substitution
				cur.execute("""
                    INSERT INTO players (
                        player_id,
                        player_name
                    ) VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;		
                """ , (
                    entry['substitution']['replacement']['id'],
                    entry['substitution']['replacement']['name']
                ))
                
				cur.execute("""
					INSERT INTO outcome (
						outcome_id,
						outcome_name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['substitution']['outcome']['id'],
					entry['substitution']['outcome']['name']
				))

				cur.execute("""
					INSERT INTO substitution (
						event_id,
						replacement,
						outcome
					) VALUES (%s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
                    entry['substitution']['replacement']['id'],
					entry['substitution']['outcome']['id']
				))
                
			case 20: # Own Goal Against
				pass
			case 21: # Foul Won
				cur.execute("""
					INSERT INTO foul_won (
						event_id,
						defensive,
                        advantage,
						penalty
					) VALUES (%s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['foul_won']['defensive'] if entry.get('foul_won') and entry['foul_won'].get('defensive') else False,
                    entry['foul_won']['advantage'] if entry.get('foul_won') and entry['foul_won'].get('advantage') else False,
                    entry['foul_won']['penalty'] if entry.get('foul_won') and entry['foul_won'].get('penalty') else False,
				))
                
			case 22: # Foul Committed
				if entry.get('foul_committed'):
					if entry['foul_committed'].get('type'):
						cur.execute("""
							INSERT INTO foul_types (
								type_id,
								type_name
							) VALUES (%s, %s)
							ON CONFLICT DO NOTHING;		
						""" , (
							entry['foul_committed']['type']['id'],
							entry['foul_committed']['type']['name']
						))
					if entry['foul_committed'].get('card'):
						cur.execute("""
							INSERT INTO cards (
								card_id,
								card_name
							) VALUES (%s, %s)
							ON CONFLICT DO NOTHING;		
						""" , (
							entry['foul_committed']['card']['id'],
							entry['foul_committed']['card']['name']
						))
				cur.execute("""
					INSERT INTO foul_committed (
						event_id,
						counterpress,
						offensive,
						foul_type,
						advantage,
						penalty,
						card_id
					) VALUES (%s, %s, %s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry.get('counterpress', False),
					entry['foul_committed'].get('offensive', False) if entry.get('foul_committed') else False,
					entry['foul_committed']['type']['id'] if entry.get('foul_committed') and entry['foul_committed'].get('type') else None,
					entry['foul_committed'].get('advantage', False) if entry.get('foul_committed') else False,
					entry['foul_committed'].get('penalty', False) if entry.get('foul_committed') else False,
					entry['foul_committed']['card']['id'] if entry.get('foul_committed') and entry['foul_committed'].get('card') else None
				))

			case 23: # Goal Keeper
				if entry['goalkeeper'].get('outcome'):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['goalkeeper']['outcome']['id'],
						entry['goalkeeper']['outcome']['name']
					))

				cur.execute("""
					INSERT INTO keeper_types (
						id,
						name
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['goalkeeper']['type']['id'],
					entry['goalkeeper']['type']['name']
				))

				if entry['goalkeeper'].get('body_part'):
					cur.execute("""
						INSERT INTO body_parts (
							bp_id,
							bp_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['goalkeeper']['body_part']['id'],
						entry['goalkeeper']['body_part']['name']
					))
				
				if entry['goalkeeper'].get('technique'):
					cur.execute("""
						INSERT INTO keeper_technique (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['goalkeeper']['technique']['id'],
						entry['goalkeeper']['technique']['name']
					))
				
				if entry['goalkeeper'].get('position'):
					cur.execute("""
						INSERT INTO keeper_pos (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['goalkeeper']['position']['id'],
						entry['goalkeeper']['position']['name']
					))
				
				cur.execute("""
					INSERT INTO goalkeeper (
						event_id,
						keeper_pos,
						keeper_technique,
						body_part,
						keeper_type,
						outcome
					) VALUES (%s, %s, %s, %s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['goalkeeper']['position']['id'] if entry['goalkeeper'].get('position') else None,
					entry['goalkeeper']['technique']['id'] if entry['goalkeeper'].get('technique') else None,
					entry['goalkeeper']['body_part']['id'] if entry['goalkeeper'].get('body_part') else None,
					entry['goalkeeper']['type']['id'] if entry['goalkeeper'].get('type') else None,
					entry['goalkeeper']['outcome']['id'] if entry['goalkeeper'].get('outcome') else None
				))


			case 24: # Bad Behaviour
				if entry.get('bad_behaviour') and entry['bad_behaviour'].get('card'):
					cur.execute("""
						INSERT INTO cards (
							card_id,
							card_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['bad_behaviour']['card']['id'],
						entry['bad_behaviour']['card']['name']
					))
				cur.execute("""
					INSERT INTO bad_behaviour (
						event_id,
						card_id
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['bad_behaviour']['card']['id'] if entry.get('bad_behaviour') and entry['bad_behaviour'].get('card') else None
				))
			case 25: # Own Goal For
				pass
			case 26: # Player On
				pass
			case 27: # Player Off
				cur.execute("""
					INSERT INTO player_off (
						event_id,
						permanent
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['player_off'].get('permanent', False) if entry.get('player_off') else False
				))
			case 28: # Shield
				pass
			case 30: # Pass
				if entry.get('pass') and entry['pass'].get('recipient'):
					cur.execute("""
						INSERT INTO players (
							player_id,
							player_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['recipient']['id'],
						entry['pass']['recipient']['name']
					))
				if entry.get('pass') and entry['pass'].get('height'):
					cur.execute("""
						INSERT INTO height (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['height']['id'],
						entry['pass']['height']['name']
					))
				if entry.get('pass') and entry['pass'].get('body_part'):
					cur.execute("""
						INSERT INTO body_parts (
							bp_id,
							bp_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['body_part']['id'],
						entry['pass']['body_part']['name']
					))
				if entry.get('pass') and entry['pass'].get('type'):
					cur.execute("""
						INSERT INTO pass_types (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['type']['id'],
						entry['pass']['type']['name']
					))
				if entry.get('pass') and entry['pass'].get('outcome'):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['outcome']['id'],
						entry['pass']['outcome']['name']
					))
				if entry.get('pass') and entry['pass'].get('technique'):
					cur.execute("""
						INSERT INTO pass_techniques (
							id,
							name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['pass']['technique']['id'],
						entry['pass']['technique']['name']
					))

				cur.execute("""
						INSERT INTO pass (
							event_id,
							recipient,
							angle,
							height,
							length,
							end_loc_x,
							end_loc_y,
							assisted_shot_id,
							backheel,
							deflected,
							miscommunication,
							cross_pass,
							cut_back,
							switch,
							shot_assist,
							goal_assist,
							body_part,
							pass_type,
							outcome,
							technique
						) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						ON CONFLICT DO NOTHING;		
					""" , (
						entry['id'],
						entry['pass']['recipient']['id'] if entry['pass'].get('recipient') else None,
						entry['pass']['angle'] if entry['pass'].get('angle') else None,
						entry['pass']['height']['id'] if entry['pass'].get('height') else None,
						entry['pass']['length'] if entry['pass'].get('length') else None,
						entry['pass']['end_location'][0] if entry['pass'].get('end_location') else None,
						entry['pass']['end_location'][1] if entry['pass'].get('end_location') else None,
						entry['pass']['assisted_shot_id'] if entry['pass'].get('assisted_shot_id') else None,
						entry['pass']['backheel'] if entry['pass'].get('backheel') else False,
						entry['pass']['deflected'] if entry['pass'].get('deflected') else False,
						entry['pass']['miscommunication'] if entry['pass'].get('miscommunication') else False,
						entry['pass']['cross_pass'] if entry['pass'].get('cross_pass') else False,
						entry['pass']['cut_back'] if entry['pass'].get('cut_back') else False,
						entry['pass']['switch'] if entry['pass'].get('switch') else False,
						entry['pass']['shot_assist'] if entry['pass'].get('shot_assist') else False,
						entry['pass']['goal_assist'] if entry['pass'].get('goal_assist') else False,
						entry['pass']['body_part']['id'] if entry['pass'].get('body_part') else None,
						entry['pass']['type']['id'] if entry['pass'].get('type') else None,
						entry['pass']['outcome']['id'] if entry['pass'].get('outcome') else None,
						entry['pass']['technique']['id'] if entry['pass'].get('technique') else None,
					))
			case 33: # 50/50
				if entry.get("50_50") and entry['50_50'].get('outcome'):
					cur.execute("""
                            INSERT INTO outcome (
                                outcome_id,
                                outcome_name
                            ) VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;		
                        """ , (
                            entry['50_50']['outcome']['id'],
                            entry['50_50']['outcome']['name']
                        ))
					
				cur.execute("""
					INSERT INTO fifty_fifty (
						event_id,
						outcome_id
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['50_50']['outcome']['id'] if entry.get('50_50') and entry['50_50'].get('outcome',()) else None
				))  
			case 34: # Half End
				cur.execute("""
					INSERT INTO half_end (
						event_id,
						early_video_end,
						match_suspended
					) VALUES (%s, %s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['early_video_end'] if entry.get('early_video_end') else False,
					entry['match_suspended'] if entry.get('match_suspended') else False
				))
			case 35: # Starting XI
				pass
			case 36: # Tactical Shift
				pass
			case 37: # Error
				pass
			case 38: # Miscontrol
				cur.execute("""
					INSERT INTO miscontrol (
						event_id,
						aerial_won
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['aerial_won'] if entry.get('aerial_won') else False
				))
			case 39: # Dribbled Past
				cur.execute("""
					INSERT INTO dribbled_past (
						event_id,
						counterpress
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['counterpress'] if entry.get('counterpress') else False
				))
			case 40: # Injury Stoppage
				cur.execute("""
					INSERT INTO injury_stoppage (
						event_id,
						in_chain
					) VALUES (%s, %s)
					ON CONFLICT DO NOTHING;		
				""" , (
					entry['id'],
					entry['injury_stoppage']['in_chain'] if entry.get('injury_stoppage') else False
				))   
			case 41: # Referee Ball-Drop
				pass
			case 42: # Ball Receipt*
				if entry.get("ball_receipt") and entry['ball_receipt'].get('outcome'):
					cur.execute("""
						INSERT INTO outcome (
							outcome_id,
							outcome_name
						) VALUES (%s, %s)
						ON CONFLICT DO NOTHING;        
					""" , (
						entry['ball_receipt']['outcome']['id'],
						entry['ball_receipt']['outcome']['name']
					))

				cur.execute("""
                        INSERT INTO ball_receipt (
                            event_id,
                            outcome_id
                        ) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;        
				""" , (
                        entry['id'],
                        entry['ball_receipt']['outcome']['id'] if entry.get('ball_receipt') and entry['ball_receipt'].get('outcome',()) else None
				))                
			case 43: # Carry
				cur.execute("""
                    INSERT INTO carry (
                        event_id,
                        end_loc_x,
                        end_loc_y
                    ) VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;        
                """ , (
                    entry['id'],
                    entry['carry']['end_location'][0],
                    entry['carry']['end_location'][1]
                ))
			case _:
				print(f"No Case made for {entry['type']['id']}:{entry['type']['name']}")


# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()