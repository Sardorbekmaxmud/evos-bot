from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from database import Database
from register import check
from location import location_handler
from messages import message_handler
from inlines import inline_handler
from config import TOKEN, DATA_BASE
import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# logging.getLogger("httpx").setLevel(logging.WARNING)
#
# logger = logging.getLogger(__name__)

db = Database(DATA_BASE)


def start_handler(update, context):
    if not update.message.from_user.is_bot:
        check(update, context)


def contact_handler(update, context):
    phone_number = update.message.contact.phone_number
    user = update.message.from_user
    db.update_user_data(user.id, "phone_number", phone_number)
    check(update, context)


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
