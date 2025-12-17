import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Pokémon × Among Bot\n\n"
        "DM me open rakho.\n\n"
        "Group command:\n"
        "/newgame"
    )

async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games[chat_id] = []

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ JOIN GAME", callback_data="join")]
    ])

    await update.message.reply_text(
        "🎮 New game started!\nJoin karo 👇",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    user = query.from_user

    if user.id in games.get(chat_id, []):
        await query.answer("Already joined", show_alert=True)
        return

    games[chat_id].append(user.id)

    await query.edit_message_text(
        f"✅ {user.first_name} joined!\nPlayers: {len(games[chat_id])}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newgame", newgame))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
