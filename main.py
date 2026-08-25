import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

class SimpleHealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHealthCheck)
    server.serve_forever()

BOT_TOKEN = "8850433468:AAG8DnOH_MzBGoF5_GDfnAtAApHsTgqJuaY"
PDF_FILE_NAME = "jozve (1).pdf"
CAPTION_TEXT = "📚 جزوه ریاضی با موفقیت ارسال شد.\nکانال ما: @PastelFinal"

TARGETS = [
    {
        "id": "@PastelFinal", 
        "text": "📢 عضویت در کانال اول", 
        "url": "https://t.me/PastelFinal"
    },
    {
        "id": "@VlP_KLID", 
        "text": "📢 عضویت در کانال دوم", 
        "url": "https://t.me/VlP_KLID"
    },
    {
        "id": -1004361916345, 
        "text": "👥 عضویت در گروه", 
        "url": "https://t.me/+2gHubFEar48yODZk"
    }
]

async def check_all_memberships(user_id: int, bot) -> bool:
    for target in TARGETS:
        try:
            member = await bot.get_chat_member(chat_id=target["id"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as err:
            print(f"Error checking {target['id']}: {err}")
            return False
    return True

def build_keyboard():
    buttons = []
    for target in TARGETS:
        buttons.append([InlineKeyboardButton(target["text"], url=target["url"])])
    buttons.append([InlineKeyboardButton("✅ در همه عضو شدم / دریافت جزوه", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_all_memberships(user_id, context.bot):
        await update.message.reply_text("عضویت شما در تمام بخش‌ها تأیید شد. در حال ارسال جزوه...")
        with open(PDF_FILE_NAME, "rb") as pdf_file:
            await context.bot.send_document(chat_id=user_id, document=pdf_file, caption=CAPTION_TEXT)
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

threading.Thread(target=run_http_server, daemon=True).start()
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_button, pattern="^check_sub$"))
app.run_polling()
