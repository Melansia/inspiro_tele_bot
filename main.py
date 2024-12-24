import random
import os
import asyncio
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import text_
import string
from dad_jokes import dad_jokes
from random_meme import meme_manager
from inspiroScript import generate_and_download_images
from secretKey import TOKEN as Tok

TOKEN: Final = Tok
BOT_USERNAME: Final = "@HunHuner_bot"


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text_.greetings["start"])


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '\n'.join(text_.commands[i] for i in text_.commands.keys())
    await update.message.reply_text(text)


async def send_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Get number of people in the group (includes bot)
    members_count = await context.bot.get_chat_members_count(chat_id)
    await update.message.reply_text(f"There are {members_count} members in this group.")

    # Get a list of chat administrators
    admins = await context.bot.get_chat_administrators(chat_id)

    # Send a message to each admin (as a demo)
    for admin in admins:
        await context.bot.send_message(chat_id=admin.user.id, text=f"Hello {admin.user.first_name}, how are you?")

    await update.message.reply_text("Message sent to group admins!")


async def inspiro_image_generator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_gif = random.choice(os.listdir("media"))
    random_bye_gif_path = os.path.join("media", f"{random_gif}")
    chat_type = update.message.chat.type
    chat_id = update.effective_chat.id
    user_names = []
    admins = []

    if chat_type == "private":
        user_names.append(update.message.from_user.first_name)
        num_images = 1
    else:
        members_count = await context.bot.get_chat_member_count(chat_id)
        admins = await context.bot.get_chat_administrators(chat_id)
        print(f"Found {members_count}")
        await context.bot.send_message(chat_id=chat_id, text="Ok, inspiration time!")
        await context.bot.send_message(chat_id=chat_id, text="Reminder! I'm working with limited resources and on a greek internet so it might take a while... Thanks for understanding!")
        for admin in admins:
            user = admin.user
            user_names.append(f"{user.first_name}")
        await context.bot.send_message(chat_id=chat_id, text=f"We gonna inspire:")
        for name in user_names:
            await context.bot.send_message(chat_id=chat_id, text=f"{name}")
        # Use MessageHandler to wait for the next message from the user
        num_images = len(user_names)

    folder_name = "inspiro_quotes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    await generate_and_download_images(num_images, folder_name, user_names)
    await asyncio.sleep(2)
    for name, admin in zip(user_names, admins if chat_type != "private" else [None] * num_images):
        image_path = os.path.join(folder_name, f"{name}_image.png")
        if os.path.exists(image_path):
            if chat_type != "private":
                # Mention admin in group chat with HTML formatting
                mentioned_user = f"<a href='tg://user?id={admin.user.id}'>{name}</a>"
                await context.bot.send_message(chat_id=chat_id, text=f"{mentioned_user}, here’s your inspiration!",
                                               parse_mode='HTML')
            else:
                # Private chat: just send the image
                await context.bot.send_message(chat_id=chat_id, text="Here’s your inspiration!")
            await context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'))
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"Image for {name} not found.")
    await asyncio.sleep(2)
    await context.bot.send_animation(chat_id=chat_id, animation=open(random_bye_gif_path, 'rb'))


async def dad_joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_id = random.choice(list(dad_jokes.keys()))
    await update.message.reply_text(dad_jokes[joke_id])


async def send_meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await meme_manager.fetch_memes(1)
    meme = meme_manager.get_random_meme()
    if meme:
        meme_url = meme['url']
        meme_title = meme['title']
        #await update.message.reply_text("Gimme a second to find a meme for ya...")
        await asyncio.sleep(1)
        #await update.message.reply_text("Found one.")
        await update.message.reply_text(f"Meme Title: {meme_title}")
        await asyncio.sleep(0.5)
        await context.bot.send_photo(chat_id=update.message.chat.id, photo=meme_url)
    else:
        await update.message.reply_text("No memes available right now.")


def clean_input(user_input):
    return user_input.lower().translate(str.maketrans('', '', string.punctuation)).strip()


# Responses
def handle_response(text: str) -> str:
    processed = clean_input(text)
    keywords = set(processed.split())

    for key in text_.convo.keys():
        key_words = set(key.split())

        # Check if all key words are present in the user input
        if key_words.issubset(keywords):
            return random.choice(text_.convo[key])

    return text_.greetings["else"]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    # app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('inspiro', inspiro_image_generator))
    app.add_handler(CommandHandler('dadjoke', dad_joke_command))
    app.add_handler(CommandHandler('meme', send_meme_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)

    # Poll the bot
    print('Polling...')
    app.run_polling(poll_interval=1)

