import os, json, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_s():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()

TOKEN = "8850433468:AAG8DnOH_MzBGoF5_GDfnAtAApHsTgqJuaY"
ADMIN = 8489885798
DB = "booklets.json"
CHANNELS = [
    {"id": "@PastelFinal", "t": "📢 کانال اول", "u": "https://t.me/PastelFinal"},
    {"id": "@VlP_KLID", "t": "📢 کانال دوم", "u": "https://t.me/VlP_KLID"},
    {"id": -1004361916345, "t": "👥 گروه", "u": "https://t.me/+2gHubFEar48yODZk"}
]

def get_db():
    if os.path.exists(DB):
        try: return json.load(open(DB, "r", encoding="utf-8"))
        except: return []
    return []

def save_db(data):
    json.dump(data, open(DB, "w", encoding="utf-8"), ensure_ascii=False)

async def is_sub(uid, bot):
    for c in CHANNELS:
        try:
            m = await bot.get_chat_member(c["id"], uid)
            if m.status not in ["member", "administrator", "creator"]: return False
        except: return False
    return True

def lock_kb():
    btns = [[InlineKeyboardButton(c["t"], url=c["u"])] for c in CHANNELS]
    btns.append([InlineKeyboardButton("✅ عضو شدم / دریافت جزوه‌ها", callback_data="chk")])
    return InlineKeyboardMarkup(btns)

def list_kb():
    b = get_db()
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"📚 {x['name']}", callback_data=f"dl_{i}")] for i, x in enumerate(b)])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if await is_sub(u.effective_user.id, c.bot):
        b = get_db()
        txt = "جزوه مورد نظر را انتخاب کنید:" if b else "✅ عضویت تایید شد.\nهنوز جزوه‌ای ثبت نشده است."
        await u.message.reply_text(txt, reply_markup=list_kb() if b else None)
    else:
        await u.message.reply_text("برای دانلود جزوه در کانال‌ها عضو شوید:", reply_markup=lock_kb())

async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    if not await is_sub(q.from_user.id, c.bot):
        await q.answer("❌ هنوز در تمام کانال‌ها و گروه عضو نشده‌اید!", show_alert=True)
        return
    if q.data == "chk":
        b = get_db()
        txt = "جزوه مورد نظر را انتخاب کنید:" if b else "✅ عضویت تایید شد.\nهنوز جزوه‌ای ثبت نشده است."
        await q.edit_message_text(txt, reply_markup=list_kb() if b else None)
    elif q.data.startswith("dl_"):
        idx = int(q.data.split("_")[1])
        b = get_db()
        if 0 <= idx < len(b):
            await c.bot.send_document(q.from_user.id, b[idx]["id"], caption=f"📚 {b[idx]['name']}\n\nکانال ما: @PastelFinal")

async def doc(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN: return
    d = u.message.document
    name = d.file_name.replace(".pdf", "") if d.file_name else "جزوه جدید"
    b = get_db()
    b.append({"name": name, "id": d.file_id})
    save_db(b)
    await u.message.reply_text(f"✅ جزوه «{name}» با موفقیت اضافه شد.", reply_markup=list_kb())

threading.Thread(target=run_s, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.Document.ALL, doc))
app.run_polling()
