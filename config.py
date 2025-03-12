import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
 

# Environment variables
API_ID = os.environ.get("API_ID","27881764")
API_HASH = os.environ.get("API_HASH","078d33056f82e3583f6161ad255af5bd")
BOT_TOKEN = os.environ.get("BOT_TOKEN","7358475016:AAFDkOqfJKjuYXEKTjRqMxCxg3qweV0jd1Y")
LOG_GROUP = os.environ.get("LOG_GROUP","-1002064001274")
MONGO_URI = os.environ.get("MONGO_URI","mongodb+srv://queenxytra:queenxytra@cluster0.ivuxz80.mongodb.net/?retryWrites=true&w=majority")

UPDATE = "t.me/solotreee"
SUPPORT = "t.me/solo_tree_support"

try:
    # Admins list
    ADMINS = [int(admin_id) for admin_id in os.environ.get("ADMINS", "").split(",") if admin_id.strip()]
    ADMINS.append(5131723020)
    ADMINS.append(5265109324)
    
except ValueError:
    raise ValueError("Your Admins list does not contain valid integers.")
