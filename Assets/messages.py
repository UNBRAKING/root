from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from Modules import BOT_USERNAME
import config


START_TXT = """
**🏏 𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐌ᴀsᴛᴇʀ 𝐁ᴏᴛ!**

Get ready to dive into the world of cricket with exciting matches and thrilling gameplay!

📋 **𝐉ᴏɪɴ 𝐀 𝐌ᴀᴛᴄʜ**: **Create or join a match with friends and see who can lead their team to victory.**

🎮 **𝐌ᴀɴᴀɢᴇ 𝐘ᴏᴜʀ 𝐓ᴇᴀᴍ**: **Strategize, set your lineup, and play the game just like a pro captain.**

🏆 **𝐂ᴏᴍᴘᴇᴛᴇ & 𝐖ɪɴ**: **Show off your cricket skills, score runs, take wickets, and claim your spot as the champion.**

**Use /help to learn more about the game.**

Let’s hit the field and play some cricket! 🚀🏏
"""

CMD_LIST = """
**𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐌ᴀsᴛᴇʀ 𝐁ᴏᴛ!**

Get ready to dive into the world of cricket with exciting matches and thrilling gameplay!
"""

EX_CMD_MSG = """
**🌟 𝐌ᴇᴍʙᴇʀs 𝐀ᴅᴅɪɴɢ:**

/add_A - add members to team A  
/add_B - add members to team B  

Eg: /add_A 1  or /add_A @username  
(Use the player number of your team)

**🌟 𝐌ᴇᴍʙᴇʀs 𝐑ᴇᴍᴏᴠɪɴɢ:**

/remove_A - remove members from team A  
/remove_B - remove members from team B  

Eg: /remove_A 2  
(Use the player number of your team)

**🌟 𝐆ᴀᴍᴇ 𝐏ʟᴀʏ 𝐂ᴏᴍᴍᴀɴᴅs:**

/startgame - to start the game  

/bowling - choose the bowling person of team A or B  
Eg: /bowling 3  
(Use the team A or B player number for bowling)

/batting - choose the batting person of team A or B  
Eg: /batting 4  
(Use the team A or B player number for batting)

/swap - to change the playing position of the current team  

/end_match - to end the current game  

/Feedback - give your feedback about the game

"""

HELP_MSG = """
**Hello! 🤗 Need some help with Cricket Master Bot? Here are some tips to get you started:**

🔹 **Join a Match**: Ready to play? Start a new match or join an existing one with your friends. Just type /start in groups.

🔹 **Manage Your Team**: Set up your lineup, choose your captain, and get ready to play. Use /startgame to get started.

🔹 **Game Instructions**: New to the game? Type /help to learn how to play and master the game.

🔹 **Feedback**: We value your input! Share your feedback with us in the support group.

🔹 **Help and Support**: If you need assistance, visit our support group or type /help.

👉 For a list of all available commands, click the "📜 𝐂ᴏᴍᴍᴀɴᴅs" button below.

**Enjoy your time with Cricket Master Bot! 🏏🚀**
"""

CUSTOM_ACTION1_MSG = """
**𝐖ᴇʟᴄᴏᴍᴇ 𝐭ᴏ 𝐂ʀɪᴄᴋᴇᴛ 𝐌ᴀsᴛᴇʀ 𝐁ᴏᴛ!**

Cricket Game Bot provide Solo play and Team play option available.
"""

CUSTOM_ACTION2_MSG = """
Soon.....
"""

START_BTN = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url=config.UPDATE),
        InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=config.SUPPORT)
    ],
    [
        InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ!", url=f"https://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")
    ],
    [
        InlineKeyboardButton("Lɪᴠᴇ ⌨ 𝐂ʜᴀᴛ ッ", url="https://t.me/SoloTree_XD_Bot")
    ]
])

HELP_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ!", url=f"https://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")
    ],
    [
        InlineKeyboardButton("📜 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="custom_action1")
    ],
    [
        InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url=config.UPDATE),
        InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=config.SUPPORT)
    ],
    [
        InlineKeyboardButton("𝐃ᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/Simba_itsme")
    ]
])

CMD_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🏠 𝐇ᴏᴍᴇ", callback_data="home"),
        InlineKeyboardButton("🕵️‍♂️ 𝐇ᴇʟᴘ", callback_data="help_back")
    ],
    [
        InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ!", url=f"https://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")
    ]
])

CUSTOM_ACTION1_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("👤 𝐒ᴏʟᴏ 𝐏ʟᴀʏ", callback_data="custom_action2"),
        InlineKeyboardButton("👥 𝐓ᴇᴀᴍ 𝐏ʟᴀʏ", callback_data="ex_cmd")
    ],
    [
        InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_back")
    ]
])

CUSTOM_ACTION2_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="custom_action1")
    ]
])

EX_CMD_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("𝐒ᴛᴀʀᴛ", callback_data="url_photo"),
        InlineKeyboardButton("𝐀ᴅᴅ", callback_data="url_video1"),
        InlineKeyboardButton("𝐑ᴇᴍᴏᴠᴇ", callback_data="url_video2")
    ],
    [
        InlineKeyboardButton("𝐒ᴛᴀʀᴛ 𝐆ᴀᴍᴇ", callback_data="url_video3"),
        InlineKeyboardButton("𝐁ᴏᴡʟɪɴɢ", callback_data="url_video4"),
        InlineKeyboardButton("𝐁ᴀᴛᴛɪɴɢ", callback_data="url_video5")
    ],
    [
        InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="custom_action1")
    ]
])

PHOTO_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="ex_cmd")]
])