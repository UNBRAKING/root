from pyromod import Client 

from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid, FloodWait
import asyncio

from Modules import app, games_collection
from Assets import files


@app.on_message(filters.command("create_team") & filters.group)
async def create_team(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return
    if message.from_user.id != game["game_host"]:
        await message.reply_text("Only the game host can create teams! 👮‍♂️")
        return

    await games_collection.update_one({"game_id": game_id}, {"$set": {"joiningA": True}})
    await message.reply_text("🎉 Team creation is underway! Join Team A by sending /join_teamA 📣")

    async def wait_and_switch():
        await asyncio.sleep(20)
        game = await games_collection.find_one({"game_id": game_id})
        if game["joiningA"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"joiningA": False, "joiningB": True}})
            await client.send_message(game_id, "⏰ Time's up for Team A! 👥 Join Team B by sending /join_teamB 📣")

        await asyncio.sleep(20)
        game = await games_collection.find_one({"game_id": game_id})
        if game["joiningB"]:
            await games_collection.update_one({"game_id": game_id}, {"$set": {"joiningB": False}})
            game_host_id = game["game_host"]
            game_host = await client.get_users(game_host_id)
            await client.send_message(game_id, f"{game_host.mention()} 👋 hey, now members are joined the teams! 🎉 Check members list using /members_list 📝", parse_mode=enums.ParseMode.HTML)

    asyncio.create_task(wait_and_switch())


@app.on_message(filters.command(["join_teamA", "join_teamB"], case_sensitive= True) & filters.group)
async def join_team(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return
    if message.from_user.id == game["game_host"]:
        await message.reply_text("You are host buddy, You can't join🥹👑")
        return
    command = message.command[0]
    team = "A" if command == "join_teamA" else "B"
    user_id = message.from_user.id

    if team == "A" and game["joiningA"]:
        if user_id in game["team_a"]["members"] or user_id in game["team_b"]["members"]:
            await message.reply_text("You are already in a Team! 🤝")
            return
        await games_collection.update_one({"game_id": game_id}, {"$push": {"team_a.members": user_id}})
        await message.reply_text(f"{message.from_user.mention()} joined Team A! ✈️", parse_mode=enums.ParseMode.HTML)

    elif team == "B" and game["joiningB"]:
        if user_id in game["team_a"]["members"] or user_id in game["team_b"]["members"]:
            await message.reply_text("You are already in a Team! 🤝")
            return
        await games_collection.update_one({"game_id": game_id}, {"$push": {"team_b.members": user_id}})
        await message.reply_text(f"{message.from_user.mention()} joined Team B! 🚀",  parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text("You can't join this team right now! ⚠️")


@app.on_message(filters.command("members_list"))
async def members_list(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return

    team_a_members = []
    for user_id in game["team_a"]["members"]:
        user = await client.get_users(user_id)
        if user.username:
            team_a_members.append(f"@{user.username}")
        else:
            team_a_members.append(user.mention)

    team_b_members = []
    for user_id in game["team_b"]["members"]:
        user = await client.get_users(user_id)
        if user.username:
            team_b_members.append(f"@{user.username}")
        else:
            team_b_members.append(user.mention)

    reply_text = (
        f"**Team A**\n" +
        '\n'.join(f"{i+1}. {member}" for i, member in enumerate(team_a_members)) +
        "\n\n" +
        f"**Team B**\n" +
        '\n'.join(f"{i+1}. {member}" for i, member in enumerate(team_b_members))
    )

    await message.reply_animation(files.TEAM_LIST, caption=reply_text, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command(["remove_A", "remove_B"], case_sensitive=True) & filters.group)
async def remove_member(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return
    if message.from_user.id != game["game_host"]:
        await message.reply_text("Only the game host can remove members! 🤝")
        return

    command = message.command[0]
    team = "A" if command == "remove_A" else "B"
    member_index = int(message.command[1]) - 1

    if team == "A":
        if member_index < len(game["team_a"]["members"]):
            await games_collection.update_one({"game_id": game_id}, {"$pull": {"team_a.members": game["team_a"]["members"][member_index]}})
            await message.reply_text(f"Member {member_index + 1} removed from Team A! ✈️")
        else:
            await message.reply_text("Invalid member index! ⚠️")
    elif team == "B":
        if member_index < len(game["team_b"]["members"]):
            await games_collection.update_one({"game_id": game_id}, {"$pull": {"team_b.members": game["team_b"]["members"][member_index]}})
            await message.reply_text(f"Member {member_index + 1} removed from Team B! 🚀")
        else:
            await message.reply_text("Invalid member index! ⚠️")


@app.on_message(filters.command(["add_A", "add_B"], case_sensitive=True) & filters.group)
async def add_member(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if not game:
        await message.reply_text("No game is going on in this chat! 🏏😔")
        return
    if message.from_user.id != game["game_host"]:
        await message.reply_text("Only the game host can add members! 🤝👥")
        return
    try:
        command = message.command[0]
        team = "A" if command == "add_A" else "B"
        if message.reply_to_message_id:
           user_input = message.reply_to_message_id 
        else: user_input = message.command[1] 
    except: 
        await message.reply_text("Please enter a valid id/username or reply to a user!")

    try:
        user_id = int(user_input)
    except ValueError:
        # If the input is not an integer, assume it's a username
        try:
            user = await client.get_users(user_input)
            user_id = user.id
        except PeerIdInvalid:
            await message.reply_text("Invalid username! Please try again. 🤔")
            return
        except FloodWait as e:
            await message.reply_text(f"Flood wait error! Please try again after {e.x} seconds. ⏰")
            return
        except Exception as e:
            await message.reply_text(f"An error occurred! {e} 🤯")
            return
    
    if user_id == game["game_host"]:
        await message.reply_text("You are host buddy, You can't join🥹👑")
        return
        
    if user_id in game["team_a"]["members"] or user_id in game["team_b"]["members"]:
        await message.reply_text("User is already in a Team! 🤝")
        return
    
    if team == "A":
        await games_collection.update_one({"game_id": game_id}, {"$push": {"team_a.members": user_id}})
        await message.reply_text(f"Member added to Team A! ✈️👍")
    elif team == "B":
        await games_collection.update_one({"game_id": game_id}, {"$push": {"team_b.members": user_id}})
        await message.reply_text(f"Member added to Team B! 🚀👊")