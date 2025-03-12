from pyromod import Client 
import asyncio, random
from pyrogram import enums 
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Modules import app, games_collection, BOT_USERNAME 
from Modules.modules.helpers import (update_game_state, 
                                     get_anime, 
                                     get_updated_game, 
                                     match_runs, warn_host, 
                                     process_game_result, 
                                     handle_innings_change, handle_over_change,
                                     listen_bowler, listen_batter,
                                     chk_batter, swap_batter,
                                     bowl_knock, bat_knock,
                                     get_invite_link
                                     )
from Modules.modules.scoreboard import generate_scorecard
from Assets import files


async def game_control(client: Client, message: Message, callback: bool = False) -> None:
    game_id = message.chat.id
    game = await get_updated_game(game_id)
    if not callback:
        await update_game_state(game_id, game)
    
    # Get updated document
    game = await get_updated_game(game_id)

    # call game_controll function in while loop for 6 balls
    ball = game["current_ball"]
    status = None
    while ball < 6:
        try:
            status = await game_controll(client, message)
            await games_collection.update_one({"game_id": game_id}, {"$inc": {"current_ball": 1}})
            ball += 1
            print(f"ball:{ball} status: {status}")
            
            matched =  await match_runs(game_id)
            print("matched:", matched)
            u_game = await get_updated_game(game_id)
            batting = u_game["batting_team"].lower()
            if matched and matched == "Tie":
                if (u_game[f"team_{batting}"]["wickets"] >= len(u_game[f"team_{batting}"]["members"]) - 1) or \
                    ((u_game["overs"] == game["current_over"]) and ball == 6):
                    status = "cancel"
                    await process_game_result(game_id, matched, message)
            elif matched and matched.endswith("wins"):
                status = "cancel"
                await process_game_result(game_id, matched, message)

            if status == "cancel":
                break
            elif status == "chng_ing":
                await games_collection.update_one({"game_id": game_id}, {"$set": {"swap": "initial"}})
                await handle_innings_change(game_id, game, message, client)
                break
            game = await get_updated_game(game_id)
            if not game: 
                status = "cancel" # game ended by /end_match so no other action
                break
            await asyncio.sleep(8)
        except Exception as e:
            print(f"Error in game control loop: {e}")
            break
    if game and status not in ["cancel", "chng_ing"]:
        OVERS = int(game["overs"])
        CR_OVER = int(game["current_over"])
        if CR_OVER != OVERS:
            scoreboard = await generate_scorecard(data = game, client= client)
            over_msg = "Here's the scorecard after over:\n\n"
            await client.send_message(message.chat.id, text= over_msg + scoreboard, parse_mode=enums.ParseMode.MARKDOWN)
            await swap_batter(game_id)
            await handle_over_change(game_id, client)
        elif CR_OVER == OVERS:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"swap": "initial"}})
            await handle_innings_change(game_id, game, message, client)


async def game_controll(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    game_id = message.chat.id
    bowling_member_id = int(game["bowling_player"])
    bowling_member = await client.get_users(bowling_member_id)
    batting_member_id = int(game["batting_player"])
    get_batter = await client.get_users(batting_member_id)
    chat_id = message.chat.id
    if not game: return
    await app.send_animation(chat_id, animation=files.BOWL_ANIME, caption= f"{bowling_member.mention(style=enums.ParseMode.MARKDOWN)} now you can send number on bot pm, You have 1 min.",  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Bowling", url=f"https://t.me/{BOT_USERNAME}")]]))
    try:
        await client.send_message(bowling_member_id, f"Current batter: {get_batter.mention(style= enums.ParseMode.MARKDOWN)}\n\nOVER BALLS = {int(game['current_ball']) + 1}")
    except: pass
    try:
        # Wait for bowling person to send number in bot pm within 1 minute
        bowling_number = int(await asyncio.wait_for(listen_bowler(client, message.chat.id, bowling_member_id), timeout=60.0))
    except asyncio.TimeoutError:
        await asyncio.sleep(10)
        # Add 6 points to current batting person if bowling person doesn't send number within 1 minute
        chat_id = message.chat.id
        if not await get_updated_game(game_id): return
        await app.send_animation(chat_id, random.choice(files.SIX), caption="No message received from bowler, Adding 6 points to Batting Team")
        await games_collection.update_one(
            {"game_id": game_id},
            {
                "$inc": {
                    f"team_{game['batting_team'].lower()}.score": 6,
                    f"team_{game['batting_team'].lower()}.balls_played": 1,
                    f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.balls_faced": 1,
                    f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.extra": 1
                },
                "$push": {
                    f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.over_outcome": "-"
                }
            }
        )
        chk = await bowl_knock(game_id, client)
        if chk: return "cancel"
        return
    try:
        # Send bowling number to host pm
        bowling_member = await client.get_users(bowling_member_id)
        link = await get_invite_link(chat_id)
        await client.send_message(game["game_host"], f"{bowling_member.mention(style=enums.ParseMode.MARKDOWN)} sent number: {bowling_number}\n\n OVER BALLS = {int(game['current_ball']) + 1} 🏏👀🎯", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Group ⌂", url=link)]]))
    except:
        pass

    # Ask batting person to send number
    await client.send_animation(message.chat.id, animation=files.BAT_ANIME, caption=f"Now Batter: {get_batter.mention(style= enums.ParseMode.MARKDOWN)} can send number (0-6)\n\nOVER BALLS = {int(game['current_ball']) + 1}")
    try:
        batter_number = int(await asyncio.wait_for(listen_batter(client, message.chat.id, batting_member_id), timeout=60.0))
    except asyncio.TimeoutError:
        await asyncio.sleep(10)
        if not await get_updated_game(game_id): return "cancel"
        # deduct 6 points to current batting team if batting person doesn't send number within 1 minute
        await client.send_animation(message.chat.id, random.choice(files.SIX), caption= "No message received from batter, deducting 6 points from batting Team")
        await games_collection.update_one(
            {"game_id": game_id},
            {
                "$inc": {
                    f"team_{game['batting_team'].lower()}.score": -6,
                    f"team_{game['batting_team'].lower()}.balls_played": 1,
                    f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.balls_faced": 1,
                    f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.runs": -6
                },
                "$push": {
                    f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.over_outcome": '0'
                }
            }
        )    
        chk = await bat_knock(game_id, client)
        if chk: return chk if chk == "chng_ing" else "cancel"
        return
    await asyncio.sleep(10)
    if bowling_number != batter_number:
        file = await get_anime(batter_number)
        if not await get_updated_game(game_id): return "cancel"
        await client.send_animation(message.chat.id, file)
        
        # Update team's score and bowls played, batter's stats, and bowler's stats
        update_ops = {
            "$inc": {
                f"team_{game['batting_team'].lower()}.score": int(batter_number),
                f"team_{game['batting_team'].lower()}.balls_played": 1,
                f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.runs": int(batter_number),
                f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.balls_faced": 1,
                f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.runs_given": int(batter_number)
            },
            "$push": {
                f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.over_outcome": batter_number
            }
        }
        if batter_number == 4:
            update_ops["$inc"][f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.4s"] = 1
        elif batter_number == 6:
            update_ops["$inc"][f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.6s"] = 1
            
        await games_collection.update_one({"game_id": game_id}, update_ops)
        # swap the batter if batting number is 1,3,5
        chk = await chk_batter(game_id, int(batter_number))
        if chk: await swap_batter(game_id)
        return
    
    else:
        try:
            # batting person out
            await client.send_animation(message.chat.id, random.choice(files.OUT), 
                                        caption=f"Number matches, {get_batter.mention(style=enums.ParseMode.MARKDOWN)}")

            update_ops = {
                "$inc": {
                    f"team_{game['batting_team'].lower()}.balls_played": 1,
                    f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.balls_faced": 1,
                    f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.wickets_taken": 1,
                    f"team_{game['batting_team'].lower()}.wickets": 1
                },
                "$push": {f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.over_outcome": 'W'},
                "$set": {
                    "batting_player": None,
                    "changing_batter": True,
                    "bat_searching": True,
                    f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.out": True
                }
            }
            await games_collection.update_one({"game_id": game_id}, update_ops)
            game_host_id = game["game_host"]
            game_host = await client.get_users(game_host_id)
            
            game = await games_collection.find_one({"game_id": game_id})
            if game["innings"] == 1:
                batting = game["batting_team"].lower()
                if game[f"team_{batting}"]["wickets"] >= len(game[f"team_{batting}"]["members"]) - 1:
                    return "chng_ing"
            if game["innings"] == 2:
                batting = game["batting_team"].lower()
                if game[f"team_{batting}"]["wickets"] == len(game[f"team_{batting}"]["members"]) - 1:
                    return "cancel"

            chat_id = message.chat.id
            await app.send_message(chat_id, f"Out! Hey {game_host.mention()}, Please choose the next batsman by command /batting.", parse_mode= enums.ParseMode.HTML)
            asyncio.create_task(warn_host(game_id, client, bat= True))
            return "cancel"
        except Exception as e:
            print("Error in line 206:", e)
            return
