from telegram import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from register import check, check_data_decorator
from database import Database
from config import DATA_BASE
from methods import send_category_buttons
from send_orders import send_user_all_orders
import globals

db = Database(DATA_BASE)


@check_data_decorator
def message_handler(update, context):
    message = update.message.text
    user = update.message.from_user
    db_user = db.get_user_by_chat_id(user.id)
    state = context.user_data.get('state', 0)

    if state == 0:
        check(update, context)

    elif state == 1:
        if not db_user['lang_id']:
            if message == globals.BTN_LANG_UZ:
                db.update_user_data(user.id, "lang_id", 1)
                check(update, context)
            elif message == globals.BTN_LANG_RU:
                db.update_user_data(user.id, "lang_id", 2)
                check(update, context)
            elif message == globals.BTN_LANG_EN:
                db.update_user_data(user.id, 'lang_id', 3)
                check(update, context)
            else:
                update.message.reply_text(text=globals.TEXT_LANG_WARNING)

        elif not db_user['first_name']:
            db.update_user_data(user.id, 'first_name', message)
            check(update, context)

        elif not db_user['last_name']:
            db.update_user_data(user.id, 'last_name', message)
            check(update, context)

        elif not db_user['phone_number']:
            db.update_user_data(user.id, 'phone_number', message)
            check(update, context)

        else:
            check(update, context)

    elif state == 2:
        if message == globals.BTN_ORDER[db_user['lang_id']]:
            categories = db.get_categories_by_parent()
            buttons = send_category_buttons(categories, db_user['lang_id'])

            update.message.reply_text(
                text=globals.TEXT_CHOOSE_CATEGORY[db_user['lang_id']],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

        elif message == globals.BTN_MY_ORDERS[db_user['lang_id']]:
            send_orders = send_user_all_orders(context, db_user)
            if send_orders:
                for order in send_orders:
                    context.bot.send_message(
                        chat_id=db_user['chat_id'],
                        text=order,
                        parse_mode="HTML"
                    )
            else:
                update.message.reply_text(
                    text=globals.NO_ORDER[db_user['lang_id']]
                )

        elif message == globals.BTN_EVOS_FAMILY[db_user['lang_id']]:
            update.message.reply_photo(
                photo=open("images/evos_family.jpg", 'rb'),
                caption=globals.TEXT_EVOS_FAMILY[db_user['lang_id']],
                parse_mode="HTML"
            )

        elif message == globals.BTN_CONTACT_US[db_user['lang_id']]:
            address = db.get_company_info()
            lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
            text = globals.TEXT_CONTACT_US[db_user['lang_id']] + address[f'address_{lang_code}']
            update.message.reply_text(
                text=text,
                parse_mode="HTML"
            )
            context.bot.send_location(
                chat_id=update.message.from_user.id,
                latitude=address['latitude'],
                longitude=address['longitude']
            )

        elif message == globals.BTN_COMMENT[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.TEXT_COMMENT[db_user['lang_id']],
                parse_mode="HTML"
            )
            context.user_data['state'] = globals.STATUS['comment']

        elif message == globals.BTN_SETTINGS[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.CHOOSE_LANG,
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text=globals.BTN_LANG_UZ),
                     KeyboardButton(text=globals.BTN_LANG_RU),
                     KeyboardButton(text=globals.BTN_LANG_EN)]
                ], resize_keyboard=True)
            )
            context.user_data['state'] = globals.STATUS['settings']

    elif state == 3:
        if message == globals.BTN_LANG_UZ:
            db.update_user_data(user.id, 'lang_id', 1)
            check(update, context)
        elif message == globals.BTN_LANG_RU:
            db.update_user_data(user.id, 'lang_id', 2)
            check(update, context)
        elif message == globals.BTN_LANG_EN:
            db.update_user_data(user.id, 'lang_id', 3)
            check(update, context)
        else:
            update.message.reply_text(text=globals.TEXT_LANG_WARNING)

    elif state == 4:
        update.message.reply_text(
            text=globals.THANKS_FOR_COMMENT[db_user['lang_id']]
        )
        db.create_suggestion(user.id, message, 0)
        check(update, context)

    else:
        update.message.reply_text(text="Assalomu alaykum!")
