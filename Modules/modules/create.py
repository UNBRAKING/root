

# Code to create games

from pyromod import Client 

from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

from database import add_served_chat
from Modules.modules.game import game_control
from Assets import files
from Modules import app, games_collection


@app.on_message(filters.command("save_game_data"))
async def save_game_data(_, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat!")
        return

    with open("res.txt", "w") as f:
        f.write(str(game))

    await message.reply_document("res.txt")


@app.on_message(filters.command("start") & filters.group)
async def start(client: Client, message: Message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("⚠️ Access Denied! You need to be a group admin to start a new game. 👥")
            return
    except:
        await message.reply_text("⚠️ Access Denied! You need to be a group admin to start a new game. 👥")

    game_id = message.chat.id
    if await games_collection.find_one({"game_id": game_id}):
        await message.reply_text("🚫 Game Already in Progress! Please wait for the current game to finish. 🕒")
        return

    game_host_button = InlineKeyboardButton("I'm the Host 🏏", callback_data="game_host")
    game_host_keyboard = InlineKeyboardMarkup([[game_host_button]])

    await message.reply_photo(files.START_IMG, caption= "**🎉 New Game Alert! 🎉** \n\nWho will be the game host for this match? 🤔", reply_markup=game_host_keyboard)
    await add_served_chat(message.chat.id, client)


@app.on_callback_query(filters.regex('game_host'))
async def handle_callback_query(client: Client, query: CallbackQuery):
    if query.data == "game_host":
        user_id = query.from_user.id

        game_id = query.message.chat.id
        game_host = {
    "game_id": game_id,
    "game_host": user_id,
    "team_a": {"members": [], "score": 0, "wickets": 0, "balls_played": 0, "player_stats": {}},
    "team_b": {"members": [], "score": 0, "wickets": 0, "balls_played": 0, "player_stats": {}},
    "overs": 0,
    "current_over": 0,
    "current_ball": 0,
    "bowling_team": None,
    "batting_team": None,
    "bowling_player": None,
    "batting_player": None,
    "batting_player2": None,
    "joiningA": False,
    "joiningB": False,
    "bowl_searching": False,
    "bat_searching": False,
    "game_state": "not_started",
    "innings": None,
    "changing_bowler": False,
    "changing_batter": False,
    "changing_inning": False,
    "swap": "Nothing"
}
        
        await games_collection.insert_one(game_host)
        await client.answer_callback_query(query.id, f"You are now the game host! 🎉", show_alert=True)
        await query.message.edit_caption(f"{query.from_user.mention()} is now the game host! Game host can create teams now by using /create_team. Let's get the match started! 🏏", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("startgame") & filters.group)
async def start_game(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return
    if message.from_user.id != game["game_host"]:
        await message.reply_text("Only the game host can add members! 🤝👥")
        return
    if not (game[f"team_a"]["members"] or game[f"team_b"]["members"]) or (game["joiningA"] or game["joiningB"] and not game["game_state"] == "started"):
        await message.reply_text("Choose the teams first! 🆘")
        return
    if len(game["team_a"]["members"]) < 2 or len(game["team_b"]["members"]) < 2:
        await message.reply_text("Each team must have at least 2 players to start the game! 👥")
        return
    if game["game_state"] == "started":
        await message.reply_text("The game is already started! 🏏")
        return

    overs_buttons = []
    for i in range(1, 8):
        overs_buttons.append(InlineKeyboardButton(f"{i} overs", callback_data=f"overs_{i}"))

    overs_keyboard = InlineKeyboardMarkup([overs_buttons[i:i+3] for i in range(0, 7, 3)])

    await message.reply_text("How many overs do you want for this game? ⏱️", reply_markup=overs_keyboard, quote= False)

@app.on_callback_query(filters.regex('overs_'))
async def handle_overs_callback_query(client: Client, query: CallbackQuery):
    overs = int(query.data.split("_")[1])
    game_id = query.message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if game["game_state"] == "started":
        await query.message.reply_text("The game is already started! 🏏")
        return
    if query.from_user.id != int(game["game_host"]):
        await query.answer(text= "Access Restricted ⚠️", show_alert= True)
        return    
    await games_collection.update_one({"game_id": game_id}, {"$set": {"overs": overs}})
    await client.answer_callback_query(query.id, f"You chose {overs} overs for this game! ⏱️", show_alert=True)
    bowling_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Team A", callback_data="team_a_bowling"), InlineKeyboardButton("Team B", callback_data="team_b_bowling")]
    ])
    await query.message.edit_text(f"OHOO!🎉, Let's play a {overs} overs Match !!")
    await query.message.reply_text("Now, which team will bowl first? 🤔", reply_markup=bowling_keyboard, quote = False)

@app.on_callback_query(filters.regex('team_'))
async def handle_team_bowling_callback_query(client: Client, query: CallbackQuery):
    team = query.data.split("_")[1]
    game_id = query.message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if game["game_state"] == "started":
        await query.message.reply_text("The game is already started! 🏏")
        return
    if query.from_user.id != int(game["game_host"]):
        await query.answer(text= "Access Restricted ⚠️", show_alert= True)
        return    
        
    if team == "a":
        await games_collection.update_one({"game_id": game_id}, {"$set": {"bowling_team": "A", "batting_team": "B", "bowl_searching": True}})
    elif team == "b":
        await games_collection.update_one({"game_id": game_id}, {"$set": {"bowling_team": "B", "batting_team": "A", "bowl_searching": True}})
    await query.edit_message_text(f"Team {team.upper()} will bowl first! 🎉")
    await query.message.reply_text("Now, type /bowling <member_number> to choose the bowling member! 📝", quote = False)
    

@app.on_message(filters.command("bowling") & filters.group)
async def bowling(client: Client, message: Message):
    try:
        game_id = message.chat.id
        game = await games_collection.find_one({"game_id": game_id})
        if not game:
            await message.reply_text("No game is going on in this chat! 🏏😔")
            return
        if message.from_user.id != game["game_host"]:
            await message.reply_text("Only the game host can choose the bowling member! 🤝👥")
            return
        if not game["bowl_searching"]:
            await message.reply_text("You can't choose a bowling member right now! ⏱️🚫")
            return
        if game["game_state"] == "started" and not game["changing_bowler"]:
            await message.reply_text("The game is already started! 🏏")
            return
        if not message.command[1]:
            await message.reply_text("Please provide the member number! 📝")

        member_index = int(message.command[1]) - 1
        bowling_team = game["bowling_team"]
        if bowling_team == "A":
            bowling_member_id = game["team_a"]["members"][member_index]
        elif bowling_team == "B":
            bowling_member_id = game["team_b"]["members"][member_index]
        get_bowl = await client.get_users(bowling_member_id)
        await games_collection.update_one({"game_id": game_id}, {"$set": {"bowl_searching": False, "bowling_player": bowling_member_id, "bat_searching": True}})
        await message.reply_text(f"Hey {get_bowl.mention(style= enums.ParseMode.MARKDOWN)}, now you're bowling!")

        if game["changing_bowler"] and not game["changing_inning"] and game["swap"]=="bowling":
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_bowler": False, "swap": "Nothing"}})
            await game_control(client, message, callback=True)
            return
        elif game["changing_bowler"] and not game["changing_inning"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_bowler": False}})
            await game_control(client, message)
            return
        elif game["changing_bowler"] and game["changing_inning"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_bowler": False, "changing_batter": True}})
        
        await message.reply_text("Now, type /batting <member_number> to choose the batting member!")
    except IndexError as e:
        await message.reply_text("Invalid member number! Please try again.")

@app.on_message(filters.command("batting") & filters.group)
async def batting(client: Client, message: Message):
    try:
        game_id = message.chat.id
        game = await games_collection.find_one({"game_id": game_id})
        if not game:
            await message.reply_text("No game is going on in this chat! 🏏😔")
            return
        if message.from_user.id != game["game_host"]:
            await message.reply_text("Only the game host can choose the batting member! 🤝👥")
            return
        if not game["bat_searching"]:
            await message.reply_text("You can't choose a Batting member right now! ⏱️🚫")
            return
        if game["game_state"] == "started" and not game["changing_batter"]:
            await message.reply_text("The game is already started! 🏏")
            return
        if not message.command[1]:
            await message.reply_text("Please provide the member number! 📝")

        try:
            member_index = int(message.command[1]) - 1
            batting_team = str(game["batting_team"])
            batting_member_id = game[f"team_{batting_team.lower()}"]["members"][member_index]
        except IndexError:
            await message.reply_text("Invalid member index ❌")
            
        try:
            if game[f"team_{game['batting_team'].lower()}"]["player_stats"][str(batting_member_id)]["batting"]["out"]:
                await message.reply_text(f"{batting_member_id} is already out! 🥶")
                return
        except:
            pass
        try:
            if int(game["batting_player"]) == int(batting_member_id):
                await message.reply_text("You can't choose main batter as the 2nd batting member! 😂")
                return
        except:
            pass
            
        try:
            if int(game["batting_player2"]) == int(batting_member_id):
                await message.reply_text("He is already 2nd batting member! 😂")
                return
        except:
            pass

        get_bat = await client.get_users(batting_member_id)
        if not game["batting_player"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"batting_player": batting_member_id}})
            await extra_handler(message, game, game_id, chk_srch = True)
            await message.reply_text(f"Hey {get_bat.mention()}, now you're batter!", parse_mode = enums.ParseMode.HTML)
        elif  game["batting_player"] and not game["batting_player2"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"bat_searching": False, "batting_player2": batting_member_id}})
            await message.reply_text(f"Hey {get_bat.mention()}, now you're 2nd batter!", parse_mode = enums.ParseMode.HTML)

        if game["changing_batter"] and not game["changing_inning"] and game["swap"]=="batting":
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_batter": False, "swap": "Nothing"}})
            await game_control(client, message, callback = True)
            return
        if game["changing_batter"] and not game["changing_inning"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_batter": False}})
            await game_control(client, message, callback = True)
            return
        game = await games_collection.find_one({"game_id": game_id})
        if game["changing_batter"] and game["changing_inning"] and game["batting_player2"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"changing_batter": False, "changing_inning": False}})
        game = await games_collection.find_one({"game_id": game_id})
        if game["batting_player"] and game["batting_player2"]:
            await message.reply_text("Get ready, the game is starting in 10 seconds!", quote=False)
            await extra_handler(message, game= game, game_id=game_id, start=True, client=client)
        else:
            await message.reply_text("Choose the second /batting player now!", quote=False)
    except IndexError as e:
        await message.reply_text("Invalid member number! Please try again.")

async def extra_handler(msg: Message, game: dict = None, game_id: int = None, **kwargs):
    if kwargs.get("chk_srch"):
        if game["batting_player2"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"bat_searching": False}})
            return
        
    if kwargs.get("start"):
        client: Client = kwargs.get("client")
        await asyncio.sleep(7)
        sk: Message = await client.send_sticker(msg.chat.id, sticker="CAACAgUAAxkBAAKNnGbO8Sq8vvJDEasdmqimeO5CaUUAA6kKAAJ5rxhVsXw8lCOqlEU1BA")
        await asyncio.sleep(1.2)
        await sk.delete()
        sk: Message = await client.send_sticker(msg.chat.id, sticker="CAACAgUAAxkBAAKNqWbO8WDKoeFDZ2y1K_CK8tMS7ypQAAKVDwACbm54ViF7z3b1JdMqNQQ")
        await asyncio.sleep(1.2)
        await sk.delete()
        sk: Message = await client.send_sticker(msg.chat.id, sticker="CAACAgUAAxkBAAKNoGbO8SroihCDGXWWudC8hacuS_l2AAJBAAO8ljUqqDHd2Hcpvjw1BA")
        await asyncio.sleep(1.2)
        if not game["innings"] == 2: 
            await games_collection.update_one({"game_id": game_id}, {"$set": {"game_state": "started", "innings": 1}})
        await sk.delete()       
        #start the game
        await game_control(client, msg)
