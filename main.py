import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ساخت سرور وب سبک برای رفع خطای رندر و آنلاین ماندن در            await context.bot.send_document(chat_id=user_id, document=pdf_file, caption=CAPTION_TEXT)
    else:
        await update.message.reply_text(
            "سلام! 👋\nبرای دریافت جزوه، لطفاً در هر دو کانال و گروه زیر عضو شوید و سپس دکمه تایید را لمس کنید:",
            reply_markup=build_keyboard()
        )

async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await check_all_memberships(user_id, context.bot):
        await query.edit_message_text("✅ عضویت کامل تأیید شد! در حال ارسال جزوه...")
        with open(PDF_FILE_NAME, "rb") as pdf_file:
            await context.bot.send_document(chat_id=user_id, document=pdf_file, caption=CAPTION_TEXT)
    else:
        await query.answer("❌ شما هنوز در تمام کانال‌ها و گروه عضو نشده‌اید!", show_alert=True)

if name == "main":
    # اجرای وب‌سرور در پس‌زمینه
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # اجرای ربات تلگرام
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_button, pattern="^check_sub$"))
    app.run_polling()
    
