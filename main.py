from bot import (
    Bot,
    START_MENU, 
    PROCESSING_DATA, 
    VERIFYING_EMAIL, 
    CONFIRMATION, 
    CHOSEN_COURSE, 
    AUTHENTICATION, 
    MAIN_MENU 
)
from database_manager import DatabaseManager
from re import compile
from os import getenv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, 
    CallbackQueryHandler, 
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    filters
    )

# Token del bot
load_dotenv()   
TOKEN = getenv("TOKEN")

def main() -> None:    
    database = DatabaseManager()
    database.connect()

    bot = Bot(database)

    application = Application.builder().token(TOKEN).build()
    conversation = ConversationHandler(
                    entry_points=[CommandHandler("start", bot.start)],
                    states={
                        START_MENU: [
                            CallbackQueryHandler(bot.register, pattern="^registrazione$"),
                            CallbackQueryHandler(bot.login, pattern="^login$")
                        ], 
                        PROCESSING_DATA: [
                            MessageHandler(filters.TEXT & ~filters.COMMAND, bot.receive_information),
                        ],
                        CONFIRMATION: [
                            CallbackQueryHandler(bot.confirm, pattern="^conferma$"),
                            CallbackQueryHandler(bot.go_back, pattern="^indietro$")
                        ],
                        VERIFYING_EMAIL: [
                            MessageHandler(filters.TEXT & ~filters.COMMAND, bot.verify_code)
                        ],
                        CHOSEN_COURSE: [
                            CallbackQueryHandler(bot.receive_information)
                        ],
                        AUTHENTICATION: [
                            MessageHandler(filters.TEXT & ~filters.COMMAND, bot.authentication)
                        ],
                        MAIN_MENU: [
                            CallbackQueryHandler(bot.show_menu, pattern=compile("^menu$|^conferma$")),
                            CallbackQueryHandler(bot.list_lessons, pattern="^visualizza_lezioni$"),
                            CallbackQueryHandler(bot.list_bookings, pattern="^visualizza_prenotazioni$"),
                            
                            CallbackQueryHandler(bot.book_lesson, pattern=compile("^prenota-\d+$")),
                            CallbackQueryHandler(bot.view_lesson, pattern=compile("^lezione-\d+$")),                           
                            
                            CallbackQueryHandler(bot.view_booking, pattern=compile("^prenotazione-\d+$")),
                            CallbackQueryHandler(bot.cancel_booking, pattern=compile("^annulla-\d+-\d+$")), 
                        ]
                    },
                    fallbacks=[CommandHandler("exit", bot.exit), CommandHandler("start", bot.start)]
                )
    
    application.add_handler(conversation)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()