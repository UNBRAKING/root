import os
import requests
from pyrogram import filters

from Modules import app
from config import ADMINS

async def paste(content):
    url ="https://pastebin.com/api/api_post.php"
    data = {"api_dev_key":"9Rfu50iV5l3EuRWATw7EDLuC37RED-C4","api_paste_code": content,"api_option": "paste","api_paste_format":"python"}
    response = requests.post(url, data=data)
    link=response.text
    return link

@app.on_message(filters.command("logs") & filters.user(ADMINS))
async def send_logs(_, message):
    try:
        args = message.text.split()
        if len(args) == 1:
            await message.reply_document("logs.txt")
        elif len(args) == 2 and args[1].isdigit():
            num_lines = int(args[1])
            with open("logs.txt", "r") as f:
                lines = f.readlines()[-num_lines:]
            await message.reply("".join(lines))
        elif len(args) == 2 and args[1] == "paste":
            with open("logs.txt", "r") as f:
                paste_content = "".join(f.readlines()[-2000:])
            paste_url = await paste(paste_content)
            await message.reply(f"Log file pasted to {paste_url}")
        else:
            await message.reply("Invalid arguments. Use /logs, /logs <int>, or /logs paste.")
    except FileNotFoundError:
        await message.reply("No log file found.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")