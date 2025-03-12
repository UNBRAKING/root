import asyncio
import importlib
from pyrogram import idle
from Modules.modules import ALL_MODULES

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello from Telegram Bot!'

loop = asyncio.get_event_loop()


async def cbot_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("Modules.modules." + all_module)
    print("𝖻𝗈𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎lly 𝗌𝗍𝖺𝗋𝗍")
    await idle()

if __name__ == "__main__":
#   just add `#` below(2 Lines only) to remove web service if not deploying on koyeb. 
#   Also change web to worker in `procfile` file.⚠️
  #  import threading
   # threading.Thread(target=app.run, args=('0.0.0.0', 8000)).start()
    loop.run_until_complete(cbot_boot()) # Do not edit
