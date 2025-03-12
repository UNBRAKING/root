from pyromod import Client 

from pyrogram import filters, enums
from pyrogram.types import Message

from Modules import app, games_collection

@app.on_message(filters.command(["totalpoints", "score"]) & filters.group)
async def total_points(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat!")
        return
    if not game["game_state"] == "started":
        await message.reply_text("The game is not started yet! 🏏")
        return

    scoreboard = await generate_scorecard(data = game, client= client)
    await message.reply_text(scoreboard, parse_mode=enums.ParseMode.MARKDOWN)


async def generate_scorecard(data, client: Client):
    scorecard = ""
    
    # Team A
    scorecard += "╭━─━─━─━─≪✠≫─━─━─━─━╮\n\n───────⊱ Tᴇᴀᴍ - A ⊰──────\n\n"
    for user_id, player_stats in data["team_a"]["player_stats"].items():
        user = await client.get_users(user_id)
        first_name = user.first_name
        batting_stats = player_stats.get("batting", {})
        runs = batting_stats.get("runs", 0)
        balls_faced = batting_stats.get("balls_faced", 0)
        scorecard += f"✴️ {first_name} = {runs}({balls_faced})\n"
        
        bowling_stats = player_stats.get("bowling", {})
        over_outcome = bowling_stats.get("over_outcome", [])
        if over_outcome:
            for i in range(0, len(over_outcome), 6):
                over = over_outcome[i:i+6]
                scorecard += f" ╰⊚ ({', '.join(str(x) for x in over)})\n"
        scorecard += "\n"
    
    total_balls_played = data["team_a"]["balls_played"]
    overs_played = total_balls_played // 6
    balls_played = total_balls_played % 6
    scorecard += f"╭──────── • ◆ • ─────────\nᴛᴇᴀᴍ A sᴄᴏʀᴇ = {data['team_a']['score']}/{data['team_a']['wickets']} ʀᴜɴs | ᴏᴠᴇʀs: {overs_played}.{balls_played}\n╰──────── • ◆ • ─────────\n\n× •-•-•-•-•-•--•-•-•⟮ 🏏 ⟯•-•-•-•-•-•-•-•-• ×\n\n"
    
    # Team B
    scorecard += "───────⊱ Tᴇᴀᴍ - B ⊰──────\n\n"
    for user_id, player_stats in data["team_b"]["player_stats"].items():
        user = await client.get_users(user_id)
        first_name = user.first_name
        batting_stats = player_stats.get("batting", {})
        runs = batting_stats.get("runs", 0)
        balls_faced = batting_stats.get("balls_faced", 0)
        scorecard += f"✴️ {first_name} = {runs}({balls_faced})\n"
        
        bowling_stats = player_stats.get("bowling", {})
        over_outcome = bowling_stats.get("over_outcome", [])
        if over_outcome:
            for i in range(0, len(over_outcome), 6):
                over = over_outcome[i:i+6]
                scorecard += f" ╰⊚ ({', '.join(str(x) for x in over)})\n"
        scorecard += "\n"
    
    total_balls_played = data["team_b"]["balls_played"]
    overs_played = total_balls_played // 6
    balls_played = total_balls_played % 6
    scorecard += f"╭──────── • ◆ • ─────────\nᴛᴇᴀᴍ ʙ sᴄᴏʀᴇ = {data['team_b']['score']}/{data['team_b']['wickets']} ʀᴜɴs | ᴏᴠᴇʀs: {overs_played}.{balls_played}\n╰──────── • ◆ • ─────────\n\n༺═────────────────═༻\n\n"

    host = await client.get_users(int(data["game_host"]))
    scorecard += f"👑**Host**: {host.mention(style=enums.ParseMode.MARKDOWN)}"
    
    return scorecard
