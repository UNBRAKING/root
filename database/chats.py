from pyrogram import Client

from Modules import ChatDB
from Modules.modules.helpers import get_invite_link
import config

async def get_served_chats() -> list:
    chats = ChatDB.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    chat = await ChatDB.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(chat_id: int, client: Client):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    await ChatDB.insert_one({"chat_id": chat_id})

    count = len(await get_served_chats())
    try:
        chat = await client.get_chat(chat_id)
        LINK = chat.invite_link if chat.invite_link else await get_invite_link(chat_id)
        INFO = f'''
#NewChat

Total chats = [{int(count)}]
Chat Name = {chat.title} 
Link = {LINK}
'''
        await client.send_message(config.LOG_GROUP, INFO)
    except:
        pass
    return 

async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await ChatDB.delete_one({"chat_id": chat_id})
