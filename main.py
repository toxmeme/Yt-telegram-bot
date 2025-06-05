import os
import yt_dlp
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
REQUIRED_CHANNELS = os.getenv("REQUIRED_CHANNELS", "").split(",")

async def is_user_subscribed(bot, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]:
                return False
        except:
            return False
    return True

async def download_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    if not await is_user_subscribed(bot, user_id):
        msg = "برای استفاده از این ربات، لطفاً ابتدا در کانال‌های زیر عضو شوید:\n"
        msg += "\n".join(REQUIRED_CHANNELS)
        await update.message.reply_text(msg)
        return

    url = update.message.text
    await update.message.reply_text("⏳ در حال دانلود ویدیو از YouTube...")

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دانلود: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube))

print("🤖 Bot is running...")
app.run_polling()
# تغییر جزئی برای Railway Deploy
