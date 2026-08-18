import os
‎import sqlite3
‎from telegram import (
‎    Update,
‎    InlineKeyboardButton,
‎    InlineKeyboardMarkup,
‎)
‎from telegram.ext import (
‎    Application,
‎    CommandHandler,
‎    CallbackQueryHandler,
‎    MessageHandler,
‎    ContextTypes,
‎    filters,
‎)
‎
‎# =========================================================
‎# SETTINGS
‎# =========================================================
‎
‎BOT_TOKEN = ""
‎
‎# Telegram user ID kee asitti galchi
‎ADMIN_ID = 123456789
‎
‎PHONE = "0913185798"
‎
‎TOTAL_TICKETS = 6000
‎TICKET_PRICE = 200
‎
‎# Demo keessatti qofa odeeffannoo kaffaltii agarsiisa
‎PAYMENT_INFO = (
‎    "🏦 Kaffaltii Demo\n"
‎    f"📞 Odeeffannoo: {PHONE}\n"
‎    f"💰 Gatii tikeetii: {TICKET_PRICE} Birr\n\n"
‎    "⚠️ Kun demo/test dha. Kaffaltii dhugaa hin mirkaneessu."
‎)
‎
‎# Badhaasa demo
‎PRIZE_1 = "500,000 Birr"
‎PRIZE_2 = "50,000 Birr"
‎PRIZE_3 = "20,000 Birr"
‎
‎
‎# =========================================================
‎# DATABASE
‎# =========================================================
‎
‎DB = "carraa_demo.db"
‎
‎
‎def db():
‎    return sqlite3.connect(DB)
‎
‎
‎def create_database():
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute("""
‎        CREATE TABLE IF NOT EXISTS tickets (
‎            number INTEGER PRIMARY KEY,
‎            user_id INTEGER,
‎            username TEXT,
‎            status TEXT DEFAULT 'available'
‎        )
‎    """)
‎
‎    cur.execute("""
‎        CREATE TABLE IF NOT EXISTS requests (
‎            id INTEGER PRIMARY KEY AUTOINCREMENT,
‎            ticket_number INTEGER,
‎            user_id INTEGER,
‎            username TEXT,
‎            status TEXT DEFAULT 'pending'
‎        )
‎    """)
‎
‎    for n in range(1, TOTAL_TICKETS + 1):
‎        cur.execute(
‎            "INSERT OR IGNORE INTO tickets(number) VALUES(?)",
‎            (n,)
‎        )
‎
‎    con.commit()
‎    con.close()
‎
‎
‎def ticket_status(number):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        "SELECT status FROM tickets WHERE number=?",
‎        (number,)
‎    )
‎
‎    row = cur.fetchone()
‎    con.close()
‎
‎    if not row:
‎        return "available"
‎
‎    return row[0]
‎
‎
‎def reserve_ticket(number, user_id, username):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        "SELECT status FROM tickets WHERE number=?",
‎        (number,)
‎    )
‎
‎    row = cur.fetchone()
‎
‎    if not row or row[0] != "available":
‎        con.close()
‎        return False
‎
‎    cur.execute(
‎        """
‎        UPDATE tickets
‎        SET user_id=?, username=?, status='reserved'
‎        WHERE number=?
‎        """,
‎        (user_id, username, number)
‎    )
‎
‎    con.commit()
‎    con.close()
‎
‎    return True
‎
‎
‎def release_ticket(number):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        """
‎        UPDATE tickets
‎        SET user_id=NULL, username=NULL, status='available'
‎        WHERE number=?
‎        """,
‎        (number,)
‎    )
‎
‎    con.commit()
‎    con.close()
‎
‎
‎def create_request(number, user_id, username):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        """
‎        INSERT INTO requests(ticket_number,user_id,username)
‎        VALUES(?,?,?)
‎        """,
‎        (number, user_id, username)
‎    )
‎
‎    request_id = cur.lastrowid
‎
‎    con.commit()
‎    con.close()
‎
‎    return request_id
‎
‎
‎def get_request(request_id):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        """
‎        SELECT ticket_number,user_id,username,status
‎        FROM requests
‎        WHERE id=?
‎        """,
‎        (request_id,)
‎    )
‎
‎    row = cur.fetchone()
‎    con.close()
‎
‎    return row
‎
‎
‎def update_request(request_id, status):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        """
‎        UPDATE requests
‎        SET status=?
‎        WHERE id=?
‎        """,
‎        (status, request_id)
‎    )
‎
‎    con.commit()
‎    con.close()
‎
‎
‎def confirm_ticket(number):
‎    con = db()
‎    cur = con.cursor()
‎
‎    cur.execute(
‎        """
‎        UPDATE tickets
‎        SET status='sold'
‎        WHERE number=?
‎        """,
‎        (number,)
‎    )
‎
‎    con.commit()
‎    con.close()
‎
‎
‎# =========================================================
‎# TICKET GRID
‎# =========================================================
‎
‎def ticket_grid(page=0):
‎    start = page * 100 + 1
‎    end = min(start + 99, TOTAL_TICKETS)
‎
‎    keyboard = []
‎
‎    row = []
‎
‎    for number in range(start, end + 1):
‎
‎        status = ticket_status(number)
‎
‎        if status == "available":
‎            text = f"🎟️ {number}"
‎        elif status == "reserved":
‎            text = f"⏳ {number}"
‎        else:
‎            text = f"🔒 {number}"
‎
‎        row.append(
‎            InlineKeyboardButton(
‎                text,
‎                callback_data=f"ticket:{number}"
‎            )
‎        )
‎
‎        if len(row) == 5:
‎            keyboard.append(row)
‎            row = []
‎
‎    if row:
‎        keyboard.append(row)
‎
‎    navigation = []
‎
‎    if page > 0:
‎        navigation.append(
‎            InlineKeyboardButton(
‎                "⬅️ Durii",
‎                callback_data=f"page:{page-1}"
‎            )
‎        )
‎
‎    if end < TOTAL_TICKETS:
‎        navigation.append(
‎            InlineKeyboardButton(
‎                "Itti aanu ➡️",
‎                callback_data=f"page:{page+1}"
‎            )
‎        )
‎
‎    if navigation:
‎        keyboard.append(navigation)
‎
‎    keyboard.append([
‎        InlineKeyboardButton(
‎            "🏠 Menu",
‎            callback_data="menu"
‎        )
‎    ])
‎
‎    return InlineKeyboardMarkup(keyboard)
‎
‎
‎# =========================================================
‎# START
‎# =========================================================
‎
‎async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎
‎    keyboard = [
‎        [
‎            InlineKeyboardButton(
‎                "🎟️ Tikeetii Filadhu",
‎                callback_data="select"
‎            )
‎        ],
‎        [
‎            InlineKeyboardButton(
‎                "🏆 Badhaasa",
‎                callback_data="prizes"
‎            )
‎        ],
‎        [
‎            InlineKeyboardButton(
‎                "ℹ️ Odeeffannoo",
‎                callback_data="info"
‎            )
‎        ]
‎    ]
‎
‎    await update.message.reply_text(
‎        "🎉 BAGA NAGAAN DHUFTAN\n\n"
‎        "🎟️ ABBAA CARRAA ABDII\n\n"
‎        "Lakkoofsa 1 hanga 6000 keessaa filachuuf "
‎        "button armaan gadii tuqi.",
‎        reply_markup=InlineKeyboardMarkup(keyboard)
‎    )
‎
‎
‎# =========================================================
‎# BUTTONS
‎# =========================================================
‎
‎async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎
‎    query = update.callback_query
‎    await query.answer()
‎
‎    data = query.data
‎
‎    # -----------------------------------------------------
‎    # MENU
‎    # -----------------------------------------------------
‎
‎    if data == "menu":
‎
‎        keyboard = [
‎            [
‎                InlineKeyboardButton(
‎                    "🎟️ Tikeetii Filadhu",
‎                    callback_data="select"
‎                )
‎            ],
‎            [
‎                InlineKeyboardButton(
‎                    "🏆 Badhaasa",
‎                    callback_data="prizes"
‎                )
‎            ],
‎            [
‎                InlineKeyboardButton(
‎                    "ℹ️ Odeeffannoo",
‎                    callback_data="info"
‎                )
‎            ]
‎        ]
‎
‎        await query.message.edit_text(
‎            "🏠 MENU\n\n"
‎            "Maal gochuu barbaadda?",
‎            reply_markup=InlineKeyboardMarkup(keyboard)
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # SELECT
‎    # -----------------------------------------------------
‎
‎    if data == "select":
‎
‎        await query.message.edit_text(
‎            "🎟️ LAKKOOFSA CARRAA FILADHU\n\n"
‎            "🟢 Available\n"
‎            "⏳ Reserved\n"
‎            "🔒 Sold\n\n"
‎            "Fuula tokko keessatti lakkoofsa 100 argita.",
‎            reply_markup=ticket_grid(0)
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # PAGE
‎    # -----------------------------------------------------
‎
‎    if data.startswith("page:"):
‎
‎        page = int(data.split(":")[1])
‎
‎        await query.message.edit_text(
‎            f"🎟️ LAKKOOFSA {page*100+1} - "
‎            f"{min((page+1)*100, TOTAL_TICKETS)}",
‎            reply_markup=ticket_grid(page)
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # TICKET
‎    # -----------------------------------------------------
‎
‎    if data.startswith("ticket:"):
‎
‎        number = int(data.split(":")[1])
‎
‎        if ticket_status(number) != "available":
‎
‎            await query.answer(
‎                "❌ Lakkoofsi kun yeroo ammaa banaa miti.",
‎                show_alert=True
‎            )
‎
‎            return
‎
‎        user = query.from_user
‎
‎        ok = reserve_ticket(
‎            number,
‎            user.id,
‎            user.username or ""
‎        )
‎
‎        if not ok:
‎
‎            await query.answer(
‎                "❌ Namni biraa qabateera.",
‎                show_alert=True
‎            )
‎
‎            return
‎
‎        request_id = create_request(
‎            number,
‎            user.id,
‎            user.username or ""
‎        )
‎
‎        context.user_data["request_id"] = request_id
‎        context.user_data["ticket_number"] = number
‎
‎        keyboard = [
‎            [
‎                InlineKeyboardButton(
‎                    "🧾 Nagahee Ergi",
‎                    callback_data=f"receipt:{request_id}"
‎                )
‎            ],
‎            [
‎                InlineKeyboardButton(
‎                    "❌ Dhiisi",
‎                    callback_data=f"cancel:{number}"
‎                )
‎            ]
‎        ]
‎
‎        await query.message.reply_text(
‎            f"🎟️ LAKKOOFSA FILATAME: {number}\n\n"
‎            f"💰 Gatii: {TICKET_PRICE} Birr\n\n"
‎            f"{PAYMENT_INFO}\n\n"
‎            "Erga kaffaltii demo raawwatte booda "
‎            "suuraa nagahee ergi.",
‎            reply_markup=InlineKeyboardMarkup(keyboard)
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # RECEIPT
‎    # -----------------------------------------------------
‎
‎    if data.startswith("receipt:"):
‎
‎        request_id = int(data.split(":")[1])
‎
‎        context.user_data["waiting_receipt"] = request_id
‎
‎        await query.message.reply_text(
‎            "🧾 Amma suuraa nagahee ergi.\n\n"
‎            "Botichi nagahee sana gara adminitti qofa erga."
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # CANCEL
‎    # -----------------------------------------------------
‎
‎    if data.startswith("cancel:"):
‎
‎        number = int(data.split(":")[1])
‎
‎        release_ticket(number)
‎
‎        await query.message.reply_text(
‎            f"❌ Tikeetii {number} dhiifameera.\n\n"
‎            "Yoo barbaadde lakkoofsa biraa filadhu."
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # ADMIN CONFIRM
‎    # -----------------------------------------------------
‎
‎    if data.startswith("confirm:"):
‎
‎        if query.from_user.id != ADMIN_ID:
‎
‎            await query.answer(
‎                "⛔ Admin qofaaf.",
‎                show_alert=True
‎            )
‎
‎            return
‎
‎        request_id = int(data.split(":")[1])
‎
‎        request = get_request(request_id)
‎
‎        if not request:
‎
‎            await query.answer(
‎                "Request hin argamne.",
‎                show_alert=True
‎            )
‎
‎            return
‎
‎        number, user_id, username, status = request
‎
‎        update_request(request_id, "approved")
‎        confirm_ticket(number)
‎
‎        await query.message.reply_text(
‎            f"✅ REQUEST MIRKAA'EE\n\n"
‎            f"🎟️ Tikeetii: {number}\n"
‎            f"👤 User ID: {user_id}"
‎        )
‎
‎        # Maamilaaf ergi
‎        try:
‎
‎            await context.bot.send_message(
‎                chat_id=user_id,
‎                text=(
‎                    "🎉 Tikeetiin kee mirkanaa'eera!\n\n"
‎                    f"🎟️ Lakkoofsa: {number}\n\n"
‎                    "🏆 ABBAA CARRAA ABDII\n\n"
‎                    f"🥇 Carraa 1ffaa: {PRIZE_1}\n"
‎                    f"🥈 Carraa 2ffaa: {PRIZE_2}\n"
‎                    f"🥉 Carraa 3ffaa: {PRIZE_3}\n\n"
‎                    "🙏 Galatoomaa waan nu filattaniif!"
‎                )
‎            )
‎
‎        except Exception as e:
‎
‎            await query.message.reply_text(
‎                f"⚠️ Maamilatti erguun dadhabame: {e}"
‎            )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # ADMIN REJECT
‎    # -----------------------------------------------------
‎
‎    if data.startswith("reject:"):
‎
‎        if query.from_user.id != ADMIN_ID:
‎
‎            await query.answer(
‎                "⛔ Admin qofaaf.",
‎                show_alert=True
‎            )
‎
‎            return
‎
‎        request_id = int(data.split(":")[1])
‎
‎        request = get_request(request_id)
‎
‎        if not request:
‎            return
‎
‎        number, user_id, username, status = request
‎
‎        update_request(request_id, "rejected")
‎        release_ticket(number)
‎
‎        await query.message.reply_text(
‎            f"❌ REQUEST DIDAME\n\n"
‎            f"🎟️ Tikeetii: {number}"
‎        )
‎
‎        try:
‎
‎            await context.bot.send_message(
‎                chat_id=user_id,
‎                text=(
‎                    "❌ Dhiifama.\n\n"
‎                    "Nagaheen kee yeroo ammaa "
‎                    "hin mirkanoofne.\n\n"
‎                    "Mee admin qunnami."
‎                )
‎            )
‎
‎        except Exception:
‎            pass
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # PRIZES
‎    # -----------------------------------------------------
‎
‎    if data == "prizes":
‎
‎        await query.message.reply_text(
‎            "🏆 BADHAASA\n\n"
‎            f"🥇 Carraa 1ffaa — {PRIZE_1}\n"
‎            f"🥈 Carraa 2ffaa — {PRIZE_2}\n"
‎            f"🥉 Carraa 3ffaa — {PRIZE_3}\n\n"
‎            f"🎟️ Gatiin tikeetii: {TICKET_PRICE} Birr"
‎        )
‎
‎        return
‎
‎    # -----------------------------------------------------
‎    # INFO
‎    # -----------------------------------------------------
‎
‎    if data == "info":
‎
‎        await query.message.reply_text(
‎            "ℹ️ ODEEFFANNOO\n\n"
‎            "🎟️ Lakkoofsa: 1–6000\n"
‎            f"💰 Gatii: {TICKET_PRICE} Birr\n"
‎            f"📞 Bilbila: {PHONE}\n\n"
‎            "🧾 Nagahee maamilaa admin qofaatu ilaala.\n"
‎            "✅ Admin erga mirkaneessee booda "
‎            "tikeetiin maamilatti deema."
‎        )
‎
‎        return
‎
‎
‎# =========================================================
‎# RECEIPT PHOTO HANDLER
‎# =========================================================
‎
‎async def receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎
‎    user = update.effective_user
‎
‎    request_id = context.user_data.get("waiting_receipt")
‎
‎    if not request_id:
‎
‎        await update.message.reply_text(
‎            "❗ Dura lakkoofsa tikeetii filadhu."
‎        )
‎
‎        return
‎
‎    request = get_request(request_id)
‎
‎    if not request:
‎
‎        await update.message.reply_text(
‎            "❌ Request hin argamne."
‎        )
‎
‎        return
‎
‎    number, user_id, username, status = request
‎
‎    # Admin buttons
‎    keyboard = [
‎        [
‎            InlineKeyboardButton(
‎                "✅ MIRKANEESSI",
‎                callback_data=f"confirm:{request_id}"
‎            )
‎        ],
‎        [
‎            InlineKeyboardButton(
‎                "❌ DIDDI",
‎                callback_data=f"reject:{request_id}"
‎            )
‎        ]
‎    ]
‎
‎    caption = (
‎        "🧾 NAGAAHEE HAARAA\n\n"
‎        f"🎟️ Tikeetii: {number}\n"
‎        f"👤 User ID: {user.id}\n"
‎        f"👤 Username: @{username if username else 'Hin qabu'}\n\n"
‎        "⚠️ Admin qofa ilaala."
‎    )
‎
‎    try:
‎
‎        await context.bot.send_photo(
‎            chat_id=ADMIN_ID,
‎            photo=update.message.photo[-1].file_id,
‎            caption=caption,
‎            reply_markup=InlineKeyboardMarkup(keyboard)
‎        )
‎
‎        await update.message.reply_text(
‎            "✅ Nagaheen kee gara adminitti ergameera.\n\n"
‎            "⏳ Mee mirkaneessa admin eegi."
‎        )
‎
‎        context.user_data["waiting_receipt"] = None
‎
‎    except Exception as e:
‎
‎        await update.message.reply_text(
‎            f"❌ Nagahee ergina irratti rakkoo: {e}"
‎        )
‎
‎
‎# =========================================================
‎# TEXT HANDLER
‎# =========================================================
‎
‎async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎
‎    await update.message.reply_text(
‎        "Mee button menu keessaa fayyadami.\n\n"
‎        "/start"
‎    )
‎
‎
‎# =========================================================
‎# ADMIN COMMAND
‎# =========================================================
‎
‎async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎
‎    if update.effective_user.id != ADMIN_ID:
‎
‎        await update.message.reply_text(
‎            "⛔ Ati admin miti."
‎        )
‎
‎        return
‎
‎    await update.message.reply_text(
‎        "👑 ADMIN PANEL\n\n"
‎        "Nagahee haaraan yoo dhufe "
‎        "asuma irratti siif mul'ata.\n\n"
‎        "Buttons:\n"
‎        "✅ Mirkaneessi\n"
‎        "❌ Diddi"
‎    )
‎
‎
‎# =========================================================
‎# MAIN
‎# =========================================================
‎
‎def main():
‎
‎    create_database()
‎
‎    app = Application.builder().token(BOT_TOKEN).build()
‎
‎    app.add_handler(
‎        CommandHandler("start", start)
‎    )
‎
‎    app.add_handler(
‎        CommandHandler("admin", admin)
‎    )
‎
‎    app.add_handler(
‎        CallbackQueryHandler(buttons)
‎    )
‎
‎    app.add_handler(
‎        MessageHandler(
‎            filters.PHOTO,
‎            receipt_photo
‎        )
‎    )
‎
‎    app.add_handler(
‎        MessageHandler(
‎            filters.TEXT & ~filters.COMMAND,
‎            text_handler
‎        )
‎    )
‎
‎    print("================================")
‎    print("ABBAA CARRAA ABDII BOT")
‎    print("Bot jalqabame...")
‎    print("================================")
‎
‎    app.run_polling()
‎
‎
‎if __name__ == "__main__":
‎    main()
‎