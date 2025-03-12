from pyromod import Client 

from pyrogram import filters, enums
from pyrogram.types import Message

from Modules import app, games_collection
from Modules.modules.helpers import handle_innings_change


@app.on_message(filters.command("end_match") & filters.group)
async def end_match(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if (member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]) and \
            (message.from_user.id != game["game_host"]):
            await message.reply_text("⚠️ Access Denied! You need to be a group admin or game host to end the match. 👥")
            return
    except Exception as e:
        # print(e)
        await message.reply_text("⚠️ Access Denied! You need to be a group admin or game host to end the match. 👥")

    if not game:
        await message.reply_text("🤔 No match is currently going on in this group.")
        return
    sk = await end_game(game_id)
    if sk: 
        await message.reply_text("🏏 Match ended successfully!")
    else:
        await message.reply_text("Failed to end match 🫤")

async def end_game(game_id):
    try:
        await games_collection.delete_one({"game_id": game_id})
        return True
    except:
        return False
    
@app.on_message(filters.command("swap") & filters.group)
async def swap_inning(client: Client, message: Message):
    game_id = message.chat.id
    game = await games_collection.find_one({"game_id": game_id})
    if message.from_user.id != game["game_host"]:
        await message.reply_text("Only the game host can swap innings! 🤝👥")
        return
    if not game:
        await message.reply_text("🤔 No match is currently going on in this group.")
        return     
    if not game["swap"] == "initial":
        await message.reply_text("You can't swap innings now ❌")
        return  
    await games_collection.update_one({"game_id": game_id}, {"$set": {"swap": "final"}})
    await handle_innings_change(game_id, game, message, client)