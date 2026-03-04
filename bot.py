import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import cursor, conn

TOKEN = os.environ.get("BOT_TOKEN")

GROUP_ID = -100XXXXXXXXXX  # replace with your group id

TOPICS = {
"pagandahan":8,
"pagwapuhan":10,
"mata_f":26,
"mata_m":15
}

slots = {
8:[],
10:[],
26:[],
15:[]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard=[
        [InlineKeyboardButton("Male",callback_data="male")],
        [InlineKeyboardButton("Female",callback_data="female")]
    ]

    await update.message.reply_text(
        "Welcome to PASIKATAN 🔥\nChoose gender:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    gender=query.data
    context.user_data["gender"]=gender

    if gender=="female":
        keyboard=[
            [InlineKeyboardButton("PAGANDAHAN",callback_data="pagandahan")],
            [InlineKeyboardButton("MATA MATAHAN",callback_data="mata_f")]
        ]
    else:
        keyboard=[
            [InlineKeyboardButton("PAGWAPUHAN",callback_data="pagwapuhan")],
            [InlineKeyboardButton("MATA MATAHAN",callback_data="mata_m")]
        ]

    await query.edit_message_text(
        "Choose the game:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    game=query.data
    topic=TOPICS[game]

    players=len(slots[topic])

    if players>=4:
        await query.edit_message_text(
            "Game is full. Try next round."
        )
        return

    context.user_data["topic"]=topic

    await query.edit_message_text(
        f"Slots: {players}/4\nSend your best photo."
    )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo=update.message.photo[-1].file_id
    context.user_data["photo"]=photo

    keyboard=[
        [InlineKeyboardButton("Confirm",callback_data="confirm")],
        [InlineKeyboardButton("Change",callback_data="change")]
    ]

    await update.message.reply_photo(
        photo,
        caption="Confirm this photo?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query=update.callback_query
    await query.answer()

    user=query.from_user
    topic=context.user_data["topic"]
    photo=context.user_data["photo"]

    slots[topic].append(user.id)

    cursor.execute(
        "INSERT INTO players VALUES(?,?,?,?,0)",
        (user.id,user.username,photo,topic)
    )
    conn.commit()

    await query.edit_message_text("Application received!")

async def post_players(context):

    for topic in slots:

        players=slots[topic]

        if len(players)<2:
            continue

        cursor.execute("SELECT username,photo FROM players WHERE topic=?",(topic,))
        data=cursor.fetchall()

        for p in data:

            await context.bot.send_photo(
                chat_id=GROUP_ID,
                message_thread_id=topic,
                photo=p[1],
                caption=f"🔥 PASIKATAN ENTRY\n\nPlayer: @{p[0]}\nReact to vote!"
            )

app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(gender,pattern="male|female"))
app.add_handler(CallbackQueryHandler(game,pattern="pagandahan|pagwapuhan|mata_f|mata_m"))
app.add_handler(MessageHandler(filters.PHOTO,photo))
app.add_handler(CallbackQueryHandler(confirm,pattern="confirm"))

print("Pasikatan Bot Running")
app.run_polling()
