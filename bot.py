import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "8778426515:AAFJkJopD148bBX6iwHXEced5Np_PXCYJG8"
TARGET_URL = "https://your-domain.com"
ALLOWED_USER_ID = 8454401183


def allowed(update):
    return (
        update.effective_user
        and update.effective_user.id == ALLOWED_USER_ID
    )


def menu():
    keyboard = [
        [
            InlineKeyboardButton("🟢 Server Status", callback_data="status"),
            InlineKeyboardButton("📊 Response", callback_data="response"),
        ],
        [
            InlineKeyboardButton("🔔 Start Monitor", callback_data="start_monitor"),
            InlineKeyboardButton("❌ Stop Monitor", callback_data="stop_monitor"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def check_server():
    try:
        r = requests.get(TARGET_URL, timeout=10)

        return (
            f"🖥️ <b>Server Monitor</b>\n\n"
            f"🌐 URL: <code>{TARGET_URL}</code>\n"
            f"📡 HTTP: <code>{r.status_code}</code>\n"
            f"⏱️ Response: <code>{r.elapsed.total_seconds():.2f}s</code>\n\n"
            + ("🟢 <b>SERVER ONLINE</b>" if r.ok
               else "🟠 <b>SERVER ERROR</b>")
        )

    except requests.RequestException:
        return (
            "🖥️ <b>Server Monitor</b>\n\n"
            "🔴 <b>SERVER UNREACHABLE</b>"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    await update.message.reply_text(
        "🛡️ <b>My Server Monitor</b>\n\n"
        "আপনার সার্ভার monitoring করতে নিচের button ব্যবহার করুন।",
        reply_markup=menu(),
        parse_mode="HTML",
    )


async def monitor_job(context: ContextTypes.DEFAULT_TYPE):
    text = check_server()

    await context.bot.send_message(
        chat_id=ALLOWED_USER_ID,
        text="🔔 <b>Automatic Check</b>\n\n" + text,
        parse_mode="HTML",
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ALLOWED_USER_ID:
        return

    if query.data in ("status", "response", "refresh"):
        await query.edit_message_text(
            check_server(),
            reply_markup=menu(),
            parse_mode="HTML",
        )

    elif query.data == "start_monitor":

        # আগে একই job থাকলে নতুনটি তৈরি না করা
        jobs = context.job_queue.get_jobs_by_name("server_monitor")

        if jobs:
            message = "🔔 Monitoring ইতিমধ্যেই চালু আছে।"
        else:
            context.job_queue.run_repeating(
                monitor_job,
                interval=300,  # প্রতি 5 মিনিটে
                first=5,
                name="server_monitor",
            )
            message = "🔔 <b>Monitoring Started</b>\nপ্রতি ৫ মিনিটে server check হবে।"

        await query.edit_message_text(
            message,
            reply_markup=menu(),
            parse_mode="HTML",
        )

    elif query.data == "stop_monitor":

        jobs = context.job_queue.get_jobs_by_name("server_monitor")

        for job in jobs:
            job.schedule_removal()

        await query.edit_message_text(
            "❌ <b>Monitoring Stopped</b>",
            reply_markup=menu(),
            parse_mode="HTML",
        )


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🛡️ Server Monitor Bot Started")
    app.run_polling()


if name == "main":
    main()
