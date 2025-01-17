from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import DATA_BASE
from database import Database
from methods import send_main_menu
import globals

db = Database(DATA_BASE)


def check(update, context):
    user = update.message.from_user
    db_user = db.get_user_by_chat_id(user.id)

    if not db_user:
        db.create_user(user.id)

        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ),
             KeyboardButton(text=globals.BTN_LANG_RU),
             KeyboardButton(text=globals.BTN_LANG_EN)]
        ]
        # print("Birinchi welcome ishladi")
        update.message.reply_text(text=globals.WELCOME_TEXT)
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
        )
        context.user_data["state"] = globals.STATUS['reg']

    elif not db_user['lang_id']:
        # print("Birinchi til ishladi")
        buttons = [
            [KeyboardButton(text=globals.BTN_LANG_UZ),
             KeyboardButton(text=globals.BTN_LANG_RU),
             KeyboardButton(text=globals.BTN_LANG_EN)]
        ]
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
        )
        context.user_data["state"] = globals.STATUS['reg']

    elif not db_user['first_name']:
        # print("Birinchi ism ishladi")
        update.message.reply_text(
            text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['state'] = globals.STATUS['reg']

    elif not db_user['last_name']:
        # print("Birinchi familiya ishladi")
        update.message.reply_text(
            text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['state'] = globals.STATUS['reg']

    elif not db_user['phone_number']:
        # print("Birinchi tel ishladi")
        button = [
            [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
        ]
        update.message.reply_text(
            text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
            reply_markup=ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
        )
        context.user_data['state'] = globals.STATUS['reg']

    else:
        send_main_menu(context, user.id, db_user['lang_id'])
        context.user_data['state'] = globals.STATUS['menu']


def check_data_decorator(func):
    def inner(update, context):
        user = update.message.from_user
        db_user = db.get_user_by_chat_id(user.id)
        state = context.user_data.get('state', 0)

        if state != globals.STATUS['reg']:
            if not db_user:
                db.create_user(user.id)

                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ),
                     KeyboardButton(text=globals.BTN_LANG_RU),
                     KeyboardButton(text=globals.BTN_LANG_EN)]
                ]
                # print("Ikkinchi welcome ishladi")
                update.message.reply_text(globals.WELCOME_TEXT)
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
                )
                context.user_data['state'] = globals.STATUS['reg']

            elif not db_user['lang_id']:
                # print("Ikkinchi til ishladi")
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ),
                     KeyboardButton(text=globals.BTN_LANG_RU),
                     KeyboardButton(text=globals.BTN_LANG_EN)]
                ]
                # print("Ikkinchi tilni tanlang ishladi")
                update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
                )
                context.user_data['state'] = globals.STATUS['reg']

            elif not db_user['first_name']:
                # print("Ikkinchi ism ishladi")
                update.message.reply_text(
                    text=globals.TEXT_ENTER_FIRST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data['state'] = globals.STATUS['reg']

            elif not db_user['last_name']:
                # print("Ikkinchi familiya ishladi")
                update.message.reply_text(
                    text=globals.TEXT_ENTER_LAST_NAME[db_user['lang_id']],
                    reply_markup=ReplyKeyboardRemove()
                )
                context.user_data['state'] = globals.STATUS['reg']

            elif not db_user['phone_number']:
                # print("Ikkinchi tel ishladi")
                button = [
                    [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
                ]
                update.message.reply_text(
                    text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
                    reply_markup=ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
                )
                context.user_data['state'] = globals.STATUS['reg']

            else:
                return func(update, context)
            return False
        else:
            return func(update, context)
    return inner
