from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8850433468:AAG8DnOH_MzBGoF5_GDfnAtAApHsTgqJuaY"
CHANNEL_ID = "@PastelFinal"
PDF_FILE_NAME = "jozve (1).pdf"
CAPTION_TEXT = "📚 جزوه ریاضی با موفقیت ارسال شد.\nکانال ما: @PastelFinal"

async def check_membership(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as err:
        print(f"Error: {err}")
        return False

def build_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/PastelFinal")],
        [InlineKeyboardButton("✅ عضو شدم / دریافت جزوه", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_membership(user_id, context.bot):
        await update.message.reply_text("عضویت شما تأیید شد. در حال ارسال جزوه...")
        with open(PDF_FILE_NAME, "rb") as pdf_file:
            await context.bot.send_document(chat_id=user_id, document=pdf_file, caption=CAPTION_TEXT)
    else:
        await update.message.reply_text(
            "سلام! 👋\nبرای دریافت جزوه، ابتدا در کانال زیر عضو شوید و سپس دکمه زیر را لمس کنید:",
            reply_markup=build_keyboard()
        )

async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await check_membership(user_id, context.bot):
        await query.edit_message_text("✅ عضویت تأیید شد! در حال ارسال جزوه...")
        with open(PDF_FILE_NAME, "rb") as pdf_file:
            await context.bot.send_document(chat_id=user_id, document=pdf_file, caption=CAPTION_TEXT)
    else:
        await query.answer("❌ هنوز در کانال عضو نشده‌اید!", show_alert=True)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_button, pattern="^check_sub$"))
app.run_polling()
