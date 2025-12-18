import os
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

games = {}

ROLES = ["teamrocket", "trainer", "pikachu"]

ROLE_INFO = {
    "teamrocket": "🚀 You are TEAM ROCKET (IMPOSTOR)",
    "trainer": "🧢 You are TRAINER (CREW)",
    "pikachu": "⚡ You are PIKACHU (DEACTIVE)"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Pokémon × Among Us\n\n"
        "/join – Join game\n"
        "/startgame – Start game\n"
        "/vote <username>\n"
        "/status\n"
        "/end"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in games:
        games[chat_id] = {"players": {}, "started": False, "votes": {}}

    game = games[chat_id]

    if game["started"]:
        await update.message.reply_text("❌ Game already started")
        return

    game["players"][user.id] = {
        "name": user.username or user.first_name,
        "role": None,
        "alive": True
    }

    await update.message.reply_text(f"✅ {user.first_name} joined")

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = games.get(chat_id)

    if not game or len(game["players"]) < 3:
        await update.message.reply_text("❌ Need at least 3 players")
        return

    if game["started"]:
        await update.message.reply_text("⚠️ Game already running")
        return

    players = list(game["players"].keys())
    roles = ["teamrocket", "pikachu"] + ["trainer"] * (len(players) - 2)
    random.shuffle(roles)

    for uid, role in zip(players, roles):
        game["players"][uid]["role"] = role
        try:
            await context.bot.send_message(uid, ROLE_INFO[role])
        except:
            pass

    game["started"] = True
    await update.message.reply_text("🚀 Game started! Roles sent in DM")

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = games.get(chat_id)

    if not game or not game["started"]:
        return

    if not context.args:
        return

    target = context.args[0].lower()

    for uid, data in game["players"].items():
        if data["name"].lower() == target and data["alive"]:
            game["votes"][uid] = game["votes"].get(uid, 0) + 1
            await update.message.reply_text(f"🗳️ Vote added for {data['name']}")
            return

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = games.get(chat_id)

    if not game:
        return

    alive = [p["name"] for p in game["players"].values() if p["alive"]]
    await update.message.reply_text("👥 Alive:\n" + "\n".join(alive))

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    games.pop(chat_id, None)
    await update.message.reply_text("🛑 Game reset")

async def anti_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_date:
        chat_id = update.effective_chat.id
        user = update.effective_user
        game = games.get(chat_id)

        if game and user.id in game["players"]:
            game["players"][user.id]["alive"] = False
            await update.message.reply_text(
                f"❌ {user.first_name} forwarded message and is OUT"
            )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("startgame", startgame))
    app.add_handler(CommandHandler("vote", vote))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(MessageHandler(filters.FORWARDED, anti_forward))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
