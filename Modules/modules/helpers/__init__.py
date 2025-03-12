import datetime
from pyromod import Client 
import random, asyncio, traceback
from pyrogram import enums, filters 
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Modules import games_collection, app, scheduler
from Modules.modules.helpers.data import get_best_players
from Modules.modules.scoreboard import generate_scorecard
from Assets import files
import os

async def get_anime(run: int) -> str:
    """
    Returns the Animation link for the given run (1-6)
    """
    file_names = {
        0: random.choice(files.ZERO), 
        1: random.choice(files.ONE), 
        2: random.choice(files.TWO),  
        3: random.choice(files.THREE),
        4: random.choice(files.FOUR),  
        5: random.choice(files.FIVE), 
        6:  random.choice(files.SIX)   }
    return file_names.get(run, "UNKNOWN.mp4")


async def listen_bowler(client: Client, chat_id: int, bowler: int):
    job1 = f"warn_{bowler}1"
    job2 = f"warn_{bowler}2"
    scheduler.add_job(warn_player, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=30), args=[client, 30, chat_id, bowler, True], id=job1)
    scheduler.add_job(warn_player, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=50), args=[client, 10, chat_id, bowler, True], id=job2)

    while True:
        answer: Message = await Client.listen(self=client, chat_id=bowler)
        try:
            number = int(answer.text)
            if 1 <= number <= 6:
                try:
                    scheduler.remove_job(job1)
                except: pass
                try:
                    scheduler.remove_job(job2)
                except:
                    pass
                link = await get_invite_link(chat_id)
                if link: await client.send_message(bowler, "👍", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Group ⌂", url=link)]]))
                return number
            else:
                await client.send_message(bowler, "Please send a number between 1 and 6!")
        except ValueError:
            await client.send_message(bowler, "Please send a number!")

async def listen_batter(client: Client, chat_id: int, batter: int):
    job1 = f"warn_{batter}1"
    job2 = f"warn_{batter}2"
    scheduler.add_job(warn_player, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=30), args=[client, 30, chat_id, batter, False], id=job1)
    scheduler.add_job(warn_player, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=50), args=[client, 10, chat_id, batter, False], id=job2)
    while True:
        answer: Message = await Client.listen(self=client, chat_id=chat_id, user_id=batter, filters=filters.text)
        if answer.from_user.id == batter:
            try:
                number = int(answer.text)
                if 0 <= number <= 6:
                    try:
                        scheduler.remove_job(job1)
                    except: pass
                    try:
                        scheduler.remove_job(job2)
                    except:
                        pass
                    await answer.reply("👍")
                    return number
                else:
                    await client.send_message(chat_id, "Please send a number between 0 and 6!")
            except ValueError:
                await client.send_message(chat_id, "Please send a number!")

async def warn_player(client: Client, sldr: int, chat_id: int, user_id: int, dm=False):
    get = await client.get_users(user_id)
    game = await get_updated_game(chat_id)
    if not game: return
    await client.send_message(chat_id, f"Warning: {get.mention(style=enums.ParseMode.MARKDOWN)}, you have {sldr} seconds left to send a number!")
    if dm:
        try:
            await client.send_message(user_id, f"Warning: {get.mention(style=enums.ParseMode.MARKDOWN)}, you have {sldr} seconds left to send a number!")
        except: pass


async def warn_host(game_id: int, client: Client, swap: bool = False, bowl: bool = False, bat: bool = False):
    try:
        game = await get_updated_game(game_id)
        host = game["game_host"]
        get = await client.get_users(host)
        
        if not game:
            return
        
        await asyncio.sleep(20) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await asyncio.sleep(20) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await asyncio.sleep(20) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await asyncio.sleep(60) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await client.send_message(int(game_id), f"⚠️⚠️⚠️\n\n {get.mention(style= enums.ParseMode.MARKDOWN)}, You have 3 minutes left only")
        
        await asyncio.sleep(30) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await asyncio.sleep(30)  
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await client.send_message(int(game_id), f"⚠️⚠️⚠️\n\n {get.mention(style= enums.ParseMode.MARKDOWN)}, You have 2 minutes left only")

        await asyncio.sleep(30) 
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await asyncio.sleep(30)  
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        
        await client.send_message(int(game_id), f"⚠️⚠️⚠️\n\n {get.mention(style= enums.ParseMode.MARKDOWN)}, You have 1 minutes left only")
        
        await asyncio.sleep(60)  # 5 minutes done
        game = await get_updated_game(game_id)
        if not game or await chk_items(game_id, bowl, bat, swap):
            return
        await games_collection.delete_one({"game_id": game_id})
        await client.send_message(int(game_id), f"Game ended due to inactivity!!")
    except Exception as e:
        print(f"Error in warn_host: {e}")


async def chk_items(game_id, bowl: bool = False, bat: bool = False, swap: bool = False):
    try:
        game = await get_updated_game(game_id)
        if bowl: 
            if game["bowling_player"]: 
                return True
        if bat:
            if game["batting_player"] and game["batting_player2"]: 
                return True
        if swap:
            if game["swap"] != "initial": 
                return True
        return False
    except Exception as e:
        print(f"Error processing game result: {e}")
        traceback.print_exc()
        return False

async def match_runs(game_id):
    try:
        game = await games_collection.find_one({"game_id": game_id})
        batting = game["batting_team"]
        bowling = game["bowling_team"]
        
        # Get scores with default value 0 if None
        team_a_score = game["team_a"].get("score", 0)
        team_b_score = game["team_b"].get("score", 0)
        
        if game["innings"] == 2:
            if team_a_score == team_b_score:
                return "Tie"
            elif game[f"team_{batting.lower()}"].get("score", 0) > game[f"team_{bowling.lower()}"].get("score", 0):
                return f"{batting} wins"
            elif (game[f"team_{bowling.lower()}"].get("score", 0) > game[f"team_{batting.lower()}"].get("score", 0)) and \
                ((game[f"team_{batting.lower()}"]["wickets"] >= len(game[f"team_{batting.lower()}"]["members"]) - 1) or \
                (game["current_ball"] == 6 and int(game["overs"]) == int(game["current_over"]))):
                return f"{bowling} wins"
        return "None"
    except Exception as e:
        print(f"Error in match_runs: {e}")


async def update_game_state(game_id: int, game) -> None:
    try:
        await games_collection.update_one(
            {"game_id": game_id},
            {"$inc": {"current_over": 1}, 
             "$set": {"current_ball": 0}}
        )
    except Exception as e:
        print(f"Error updating game state: {e}")

async def get_updated_game(game_id: int) -> dict:
    try:
        data = await games_collection.find_one({"game_id": game_id})
        if not data["game_state"] == "started": return {}
        return data
    except Exception as e:
        print(f"Error getting updated game: {e}")
        return {}
    
async def get_chat_photos(chat_id):
    chat = await app.get_chat(chat_id)  
    if chat.photo:
        file_id = chat.photo.big_file_id
        path = f"pfp_{str(chat_id)[6:]}.jpg"
        path= await app.download_media(file_id, path)
        return path
    else:
        return 'Assets/pfp_Def.jpg'  # Default profile picture

async def process_game_result(game_id: int, matched: str, message: Message) -> None:
    try:
        chat_id = message.chat.id
        data = await games_collection.find_one({"game_id": game_id})
        output_file = f'score_{str(chat_id)[6:]}.jpg'
        # Get the group's profile photo
        profile_photo = await get_chat_photos(chat_id)        

        if matched == "Tie":
            chat_id = message.chat.id
            await app.send_message(chat_id, "It's a tie! 🤝")
            file = await get_best_players(data=data, Winner='Tie', output=output_file, profile= profile_photo)
            if file: await app.send_photo(chat_id, photo=output_file, caption="Tie")
        elif matched.endswith("wins"):
            chat_id = message.chat.id
            winner = matched.replace(" wins", "")
            await app.send_message(chat_id, f"🏆 Team {winner} wins this game! 🎉")
            file = await get_best_players(data=data, Winner=winner, output=output_file, profile= profile_photo)
            if file: await app.send_photo(chat_id= chat_id, photo= output_file)
            try:
                os.remove(output_file)
                os.remove(profile_photo)
            except:
                pass
            scoreboard = await generate_scorecard(data = data, client= app)
            over_msg = "Here's the scorecard after match:\n\n"
            await app.send_message(message.chat.id, text= over_msg + scoreboard, parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        print(f"Error processing game result: {e}")
        traceback.print_exc()

async def bowl_knock(game_id: int, client: Client) -> bool:
    try:
        game = await games_collection.find_one({"game_id": game_id})
        if game["current_ball"] == 5: 
            return
        output: list = game[f"team_{game['bowling_team'].lower()}"]["player_stats"][str(game['bowling_player'])]["bowling"]["over_outcome"]
        _items = output[-2:]
        if _items == ['-', '-']:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"swap": "bowling"}})
            await handle_over_change(game_id, client, swap=True)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking knock: {e}")
        traceback.print_exc()
        return False

async def bat_knock(game_id: int, client: Client):
    try:
        game = await games_collection.find_one({"game_id": game_id})
        output: list = game[f"team_{game['bowling_team'].lower()}"]["player_stats"][str(game['bowling_player'])]["bowling"]["over_outcome"]
        _items = output[-2:]
        if _items == ['0', '0']:
            output[-1] = 0
            await games_collection.update_one({"game_id": game_id}, {"$set": {
                "swap": "batting", "batting_player": None, "changing_batter": True, 
                "bat_searching": True,
                f"team_{game['batting_team'].lower()}.player_stats.{game['batting_player']}.batting.out": True,
                f"team_{game['bowling_team'].lower()}.player_stats.{game['bowling_player']}.bowling.over_outcome": output
                }})
            await games_collection.update_one({"game_id": game_id}, {"$inc": {f"team_{game['batting_team'].lower()}.wickets": 1}})
            game_host = await client.get_users(game["game_host"])
            if game["innings"] == 1:
                batting = game["batting_team"].lower()
                if game[f"team_{batting}"]["wickets"] + 1 >= len(game[f"team_{batting}"]["members"]) - 1:
                    await client.send_animation(game_id, random.choice(files.OUT), caption="Batter not responding❕")
                    return 'chng_ing'
            if game["innings"] == 2:
                batting = game["batting_team"].lower()
                if game[f"team_{batting}"]["wickets"] + 1 == len(game[f"team_{batting}"]["members"]) - 1:
                    return True
            msg = f"Hey {game_host.mention()}, it seems the current batsman is not responding, Please choose the next batsman by command /batting."
            await client.send_message(game_id, msg, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(warn_host(game_id, client, bat= True))
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking knock: {e}")
        traceback.print_exc()
        return False

async def handle_innings_change(game_id: int, game: dict, message: Message, client: Client) -> None:
    try:
        game = await get_updated_game(game_id)
        if not game["innings"] == 1:
            return
        if not game["swap"] == "final":
            await games_collection.update_one({"game_id": game_id}, {"$set": {"swap": "initial"}})
            host = int(game["game_host"])
            get = await client.get_users(host)
            await client.send_message(int(game_id), f"Hey {get.mention(style= enums.ParseMode.MARKDOWN)} !! Use swap command to change inning.\n\n⚠️You have 3 minutes only.")
            await warn_host(game_id, client, swap= True)
            return
        # Change innings
        await games_collection.update_one({"game_id": game_id}, {
            "$set": {
                "bowling_team": "B" if game["bowling_team"] == "A" else "A",
                "batting_team": "A" if game["batting_team"] == "B" else "B",
                "bowling_player": None,
                "batting_player": None,
                "batting_player2": None,
                "changing_bowler": True,
                "bowl_searching": True,
                "current_over": 0,
                "current_ball": 0,
                "innings": 2,
                "changing_inning": True,
                "swap": "Nothing"
            }
        })
        game_host_id = game["game_host"]
        game_host = await client.get_users(game_host_id)
        chat_id = message.chat.id
        await app.send_message(chat_id, f"Innings changed! Hey {game_host.mention()}, Please choose the bowler by command /bowling.", parse_mode= enums.ParseMode.HTML)
    except Exception as e:
        print(f"Error handling innings change: {e}")

async def handle_over_change(game_id: int, client: Client, swap: bool= False) -> None:
    try:
        game = await get_updated_game(game_id)
        # update bowling player
        await games_collection.update_one({"game_id": game_id}, {"$set": {"bowling_player": None, "changing_bowler": True, "bowl_searching": True}})
        game_host_id = game["game_host"]
        game_host = await client.get_users(game_host_id)
        msg = f"Over! Hey {game_host.mention()}, Please choose the next bowler by command /bowling."
        if swap: 
            msg = f"Hey {game_host.mention()}, it seems the current bowler is not responding, Please choose the next bowler by command /bowling."
        await client.send_message(game_id, msg, parse_mode= enums.ParseMode.HTML)
        await warn_host(game_id, client, bowl= True)
    except Exception as e:
        print(f"Error handling over change: {e}")

async def chk_batter(game_id, batter_number: int):
    if batter_number in [1, 3, 5]:
        return True
    return False

async def swap_batter(game_id):
    game = await games_collection.find_one({"game_id": game_id})
    await games_collection.update_one({"game_id": game_id}, {"$set": {"batting_player": int(game["batting_player2"]), "batting_player2": int(game["batting_player"])}})
    return

async def get_invite_link(chat_id):
    try:
        chat = await app.get_chat(chat_id)
        if chat.invite_link:
            link = chat.invite_link
            return link
        if chat.username:
            link = f"https://t.me/{chat.username}"
            return link
        link = await app.export_chat_invite_link(chat_id)
        return link
    except:
        return None
