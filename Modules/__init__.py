import asyncio
import logging
import time
from motor import motor_asyncio
from dotenv import load_dotenv
from pyromod import Client
import apscheduler.schedulers.asyncio as aps
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI,  ADMINS as ADMIN_IDS, LOG_GROUP

# Tg bot __init_.py


loop = asyncio.get_event_loop()
load_dotenv()
boot = time.time()


# Create a file handler
file_handler = logging.FileHandler('logs.txt')
file_handler.setLevel(logging.INFO)

# Create a formatter and set the formatter for the file handler
formatter = logging.Formatter('[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s')
file_handler.setFormatter(formatter)

# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Add the file handler to the root logger
root_logger.addHandler(file_handler)

# Now, set up the basic logging configuration
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)


app = Client(
    ":cbot:",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


client = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["cricket_bot"]
games_collection = db["games"]
ChatDB = db["Chats_DB"]
UserDB = db["User_DB"]

# Create a async scheduler
scheduler = aps.AsyncIOScheduler()


ADMIN_IDS = ADMIN_IDS
LOG_GROUP = LOG_GROUP

async def cbot_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await app.start()
    try:
        await app.send_message(int(LOG_GROUP), text= "Bot started successfully!")
    except Exception as e:
        print("Please add to your log group, and give me administrator powers!")
        print(f"Error: {e}")
    
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
    

scheduler.start()
loop.run_until_complete(cbot_bot())