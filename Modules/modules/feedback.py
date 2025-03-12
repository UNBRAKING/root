import asyncio
from pyromod import Client
from pyrogram import filters
from pyrogram.types import Message
from Modules import app
from config import LOG_GROUP

@app.on_message(filters.command("feedback"))
async def feedback(client: Client, message: Message):
    SK: Message = await message.reply_text("Please enter your feedback:")
    try:
        # Wait for the user to send the feedback message
        feedback_msg: Message = await client.listen(chat_id= message.chat.id, user_id= message.from_user.id, timeout= 180)
    except asyncio.exceptions.TimeoutError:
        await SK.edit_text("No message received, Timeout!!")
        return
    try:
        if feedback_msg:
            sent_msg = await client.forward_messages(LOG_GROUP, message.from_user.id, feedback_msg.id)
            user_info = f"User ID: {message.from_user.id}\nUsername: @{message.from_user.username}"
            feedback_info = (
                f"📣 New Feedback! 📣\n\n{user_info}"
            )
            await client.send_message(LOG_GROUP, feedback_info, reply_to_message_id= sent_msg.id)
            await message.reply_text("Thanks for your feedback! It has been sent to the log group.")
        else:
            await message.reply_text("Your feedback message cannot be empty. Please try again.")
    except Exception as e:
        try:
            await client.send_message(LOG_GROUP, e)
        except:
            print(f"An error caught during sending feedback to log channel!! Please chack log channel id properly. Error:{e}")
