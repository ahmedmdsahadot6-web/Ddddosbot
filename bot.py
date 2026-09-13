import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8778426515:AAFJkJopD148bBX6iwHXEced5Np_PXCYJG8"
TARGET_URL = "https://your-domain.com"

# শুধু আপনার নিজের Telegram user ID ব্যবহার করুন
ALLOWED_USER_ID = 8454401183


def authorized(update: Update):
    return update.effective_user.id == ALLOWED_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    await update.message.reply_text(
        "🛡️ Server Monitor Bot\n\n"
        "/status - Server status দেখুন\n"
        "/help - Help"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    try:
        response = requests.get(TARGET_URL, timeout=10)

        await update.message.reply_text(
            f"🖥️ Server Status\n\n"
            f"URL: {TARGET_URL}\n"
            f"HTTP: {response.status_code}\n"
            f"Response: {response.elapsed.total_seconds():.2f}s\n\n"
            + ("✅ Server is UP" if response.ok else "⚠️ Server returned an error")
        )

    except requests.RequestException as e:
        await update.message.reply_text(
            "🔴 Server unreachable\n"
            f"Error: {type(e).name}"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    await update.message.reply_text(
        "/status — আপনার নিজের সার্ভার পরীক্ষা করুন\n"
        "/start — Bot menu"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot started...")
    app.run_polling()


if name == "main":
    main()
