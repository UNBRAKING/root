import re
from pyrogram import filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Modules import app
from pyrogram.types import InputMediaVideo, InputMediaPhoto
from database import add_served_user
from Assets.messages import (
    START_TXT, 
    START_BTN,
    CMD_LIST,
    HELP_MSG,
    HELP_MARKUP,
    EX_CMD_MARKUP,
    EX_CMD_MSG,
    CMD_MARKUP,
    CUSTOM_ACTION1_MSG,
    CUSTOM_ACTION1_MARKUP,
    PHOTO_MARKUP,
    CUSTOM_ACTION2_MARKUP,
    CUSTOM_ACTION2_MSG,
)
from Assets import files  # Corrected import for files


@app.on_message(filters.command(["start"]) & filters.private)
async def start(client, message: Message):
    id = message.from_user.id
    await message.reply_photo(files.TEAM_LIST, caption=START_TXT, reply_markup=START_BTN)
    await add_served_user(id, client)


@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(HELP_MSG, reply_markup=HELP_MARKUP)
    await add_served_user(message.from_user.id, client)


@app.on_callback_query(filters.regex(re.compile('home|commands|help_back|ex_cmd|url_photo|url_video1|url_video2|url_video3|url_video4|url_video5|custom_action1|custom_action2|custom_action3')))
async def start_query(client, query: CallbackQuery):
    
    # Handle the "home" action
    if query.data == "home":
        await query.message.delete()
        await app.send_photo(query.message.chat.id, files.TEAM_LIST, caption=START_TXT, reply_markup=START_BTN)

    # Handle the "commands" action
    elif query.data == "commands":
        await query.message.delete()
        await app.send_message(query.message.chat.id, CMD_LIST, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=CMD_MARKUP)

    # Handle the "help_back" action
    elif query.data == "help_back":
        await query.message.delete()
        await app.send_message(query.message.chat.id, HELP_MSG, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=HELP_MARKUP)

    # Handle the "ex_cmd" action
    elif query.data == "ex_cmd":
        await query.message.delete()
        await app.send_message(query.message.chat.id, EX_CMD_MSG, reply_markup=EX_CMD_MARKUP)

    # Add new custom actions similar to "ex_cmd"

    # Handle "custom_action1"
    elif query.data == "custom_action1":
        await query.message.delete()
        await app.send_message(query.message.chat.id, CUSTOM_ACTION1_MSG, reply_markup=CUSTOM_ACTION1_MARKUP)

    # Handle "custom_action2"
    elif query.data == "custom_action2":
        await query.message.delete()
        await app.send_message(query.message.chat.id, CUSTOM_ACTION2_MSG, reply_markup=CUSTOM_ACTION2_MARKUP)

    # Handle "custom_action3"
    elif query.data == "custom_action3":
        await query.message.delete()
        await app.send_message(query.message.chat.id, CUSTOM_ACTION3_MSG, reply_markup=CUSTOM_ACTION3_MARKUP)

    # Handle the photo button action
    elif query.data == "url_photo":
        await query.message.delete()
        media = InputMediaPhoto(
            media="https://graph.org//file/d0dc43cc85a5efd399bd8.mp4",
            caption="Start a new match or join an existing one with your friends. Just type /start in groups."
        )
        await app.send_animation(query.message.chat.id, "https://graph.org//file/d0dc43cc85a5efd399bd8.mp4", caption=media.caption, reply_markup=PHOTO_MARKUP)

    # Handle the video button actions
    elif query.data == "url_video1":
        await query.message.delete()
        media = InputMediaVideo(
            media="https://graph.org/file/73cd6061f405e90bef5bd.mp4",  # Updated URL for url_video1
            caption="Eg: /add_A 1  or /add_A @username\n(Use the player number of your team)"
        )
        await app.send_video(query.message.chat.id, media.media, caption=media.caption, reply_markup=PHOTO_MARKUP)

    elif query.data == "url_video2":
        await query.message.delete()
        media = InputMediaVideo(
            media="https://graph.org/file/deb6c19be161b8c0149ce.mp4",
            caption="Eg: /remove_A 2\n(Use the player number of your team)"
        )
        await app.send_video(query.message.chat.id, media.media, caption=media.caption, reply_markup=PHOTO_MARKUP)

    elif query.data == "url_video3":
        await query.message.delete()
        media = InputMediaVideo(
            media="https://graph.org/file/1621d67b55ea082c1cf82.mp4",
            caption="/startgame - to start the game"
        )
        await app.send_video(query.message.chat.id, media.media, caption=media.caption, reply_markup=PHOTO_MARKUP)

    elif query.data == "url_video4":
        await query.message.delete()
        media = InputMediaVideo(
            media="https://graph.org/file/30247a4299926f3c933b2.mp4",
            caption="Eg: /bowling 3\n(Use the team A or B player number for bowling)"
        )
        await app.send_video(query.message.chat.id, media.media, caption=media.caption, reply_markup=PHOTO_MARKUP)

    elif query.data == "url_video5":
        await query.message.delete()
        media = InputMediaVideo(
            media="https://graph.org/file/e21efb4610c3ab1c9d20f.mp4",
            caption="Eg: /batting 4\n(Use the team A or B player number for batting)"
        )
        await app.send_video(query.message.chat.id, media.media, caption=media.caption, reply_markup=PHOTO_MARKUP)