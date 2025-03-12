import psutil
import time
from pyrogram import filters, types
from Modules import app, ADMIN_IDS, BOT_NAME
from database import get_served_chats, get_served_users

start_time = time.time()

def time_formatter(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (((str(weeks) + "ᴡ:") if weeks else "") +
           ((str(days) + "ᴅ:") if days else "") +
           ((str(hours) + "ʜ:") if hours else "") +
           ((str(minutes) + "ᴍ:") if minutes else "") +
           ((str(seconds) + "s") if seconds else ""))
    if not tmp:
        return "0s"
    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp

@app.on_message(filters.command('stats') & filters.user(ADMIN_IDS))
async def get_stats(client, msg: types.Message):
    users = await get_served_users()
    chats = await get_served_chats()

    # Calculate uptime
    uptime = time_formatter((time.time() - start_time) * 1000)

    # Get CPU and RAM usage
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    txt = f'''
**Total Stats of {BOT_NAME} :**

  • Chats: [{len(chats)}]
  • Users: [{len(users)}]
  • Uptime: {uptime}
  • CPU Usage: {cpu}%
  • RAM Usage: {ram}%
'''
    await msg.reply(txt)
