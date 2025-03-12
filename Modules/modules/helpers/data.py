from Modules.modules.helpers.logo import ScorecardGenerator
from Modules import app
import traceback


generator = ScorecardGenerator("Assets/scorecard.jpg") 

async def get_best_players(data, Winner: str, output: str, profile: str):
    try:
        result = {}

        for team_name, team_data in [('Team A', data['team_a']), ('Team B', data['team_b'])]:
            players = team_data['player_stats']

            # Sort players to find the best bowler and best batsman
            best_bowler_id = sorted(players.keys(), key=lambda player_id: (-players[player_id].get('bowling', {}).get('wickets_taken', 0), players[player_id].get('bowling', {}).get('runs_given', 0)))[0]
            get_bowler = await app.get_users(int(best_bowler_id))
            bowler_id = get_bowler.username if get_bowler.username else get_bowler.first_name[:9]
            bowling_outcomes = players[best_bowler_id].get('bowling', {}).get('over_outcome', [])
            overs_bowled_str = f"{len(bowling_outcomes) // 6}.{len(bowling_outcomes) % 6}"
            best_batsman_id = sorted(players.keys(), key=lambda player_id: players[player_id].get('batting', {}).get('runs', 0), reverse=True)[0]
            get_batter = await app.get_users(int(best_batsman_id))
            batsman_id = get_batter.username if get_batter.username else get_batter.first_name[:9]
            overs = f"{int(team_data['balls_played']) // 6}.{int(team_data['balls_played']) % 6}"
            result[team_name] = {
                'score': f"{team_data['score']}/{team_data['wickets']}",
                'overs': overs,
                'best_bowler': {
                    'player_id': bowler_id,
                    'overs': overs_bowled_str,
                    'wickets': players[best_bowler_id].get('bowling', {}).get('wickets_taken', 0),
                    'runs_given': players[best_bowler_id].get('bowling', {}).get('runs_given', 0),
                    'extra': players[best_bowler_id].get('bowling', {}).get('extra', 0),
                },
                'best_batsman': {
                    'player_id': batsman_id,
                    'runs': players[best_batsman_id].get('batting', {}).get('runs', 0),
                    'balls': players[best_batsman_id].get('batting', {}).get('balls_faced', 0),
                    'sixes': players[best_batsman_id].get('batting', {}).get('6s', 0),
                    'fours': players[best_batsman_id].get('batting', {}).get('4s', 0)
                }
            }
        generator.generate_scorecard(result, output, profile, winner = Winner)
        return "done"
    except Exception as e:
        print("Error occured while genrating scorecard:", e)
        traceback.print_exc()
        return None