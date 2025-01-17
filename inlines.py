import logging

from config import DATA_BASE
from database import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from methods import send_category_buttons, send_product_buttons
from location import location_handler
import globals

db = Database(DATA_BASE)


def inline_handler(update, context):
    query = update.callback_query
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)
    # print(data_sp)
    context.user_data['db_user'] = db_user

    if data_sp[0] == "category":
        if data_sp[1] == "product":
            # category_product_back bo'lsa ishlaydi
            # product haqida ma'lumotlardan orqaga ya'ni product lar qismiga o'tkazadi
            if data_sp[2] == "back":
                products = db.get_products_by_category(category_id=int(data_sp[3]))
                query.message.delete()
                buttons = send_product_buttons(products, db_user['lang_id'])

                clicked_button = db.get_by_parent(category_id=int(data_sp[3]))

                if clicked_button and clicked_button['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back",
                        callback_data=f"category_back_{clicked_button['parent_id']}"
                    )]
                    )
                else:
                    buttons.append(
                        [InlineKeyboardButton(
                            text="Back",
                            callback_data="category_back"
                        )]
                    )

                query.message.reply_text(
                    text=globals.TEXT_CHOOSE_CATEGORY[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )

            # category_product_back bo'lmagan holatda ishlaydi
            # aynan bitta product haqida ma'lumot chiqaradi
            else:
                if len(data_sp) == 4:
                    query.message.delete()
                    carts = context.user_data.get("carts", {})
                    carts[data_sp[2]] = carts.get(data_sp[2], 0) + int(data_sp[3])
                    context.user_data["carts"] = carts

                    categories = db.get_categories_by_parent()
                    buttons = send_category_buttons(categories, db_user['lang_id'])

                    text = f"{globals.BASKET[db_user['lang_id']]}\n\n"
                    total_price = 0
                    land_code = globals.LANGUAGE_CODE[db_user['lang_id']]

                    for cart, val in carts.items():
                        product = db.get_product_for_cart(int(cart))
                        text += f"{val} x {product[f'cat_name_{land_code}']} {product[f'name_{land_code}']}\n"
                        total_price += product['price'] * val

                    text += f"\n{globals.ALL[db_user['lang_id']]} {total_price} {globals.SUM[db_user['lang_id']]}"

                    buttons.append(
                        [InlineKeyboardButton(text=globals.BTN_BUY[db_user['lang_id']], callback_data='cart')])

                    query.message.reply_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                        parse_mode="HTML"
                    )
                else:
                    product = db.get_product_by_id(int(data_sp[2]))
                    query.message.delete()

                    caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} " + str(product['price']) + \
                              f" {globals.SUM[db_user['lang_id']]}" + \
                              f"\n{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]} " + \
                              product[f"description_{globals.LANGUAGE_CODE[db_user['lang_id']]}"]

                    buttons = [
                        [InlineKeyboardButton(text="1️⃣", callback_data=f"category_product_{data_sp[2]}_1"),
                         InlineKeyboardButton(text="2️⃣", callback_data=f"category_product_{data_sp[2]}_2"),
                         InlineKeyboardButton(text="3️⃣", callback_data=f"category_product_{data_sp[2]}_3")],

                        [InlineKeyboardButton(text="4️⃣", callback_data=f"category_product_{data_sp[2]}_4"),
                         InlineKeyboardButton(text="5️⃣", callback_data=f"category_product_{data_sp[2]}_5"),
                         InlineKeyboardButton(text="6️⃣", callback_data=f"category_product_{data_sp[2]}_6")],

                        [InlineKeyboardButton(text="7️⃣", callback_data=f"category_product_{data_sp[2]}_7"),
                         InlineKeyboardButton(text="8️⃣", callback_data=f"category_product_{data_sp[2]}_8"),
                         InlineKeyboardButton(text="9️⃣", callback_data=f"category_product_{data_sp[2]}_9")],

                        [InlineKeyboardButton(text="Back",
                                              callback_data=f"category_product_back_{product['category_id']}")]
                    ]

                    query.message.reply_photo(
                        photo=open(product['image'], 'rb'),
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                        parse_mode="HTML"
                    )

        # category_back bo'lsa ishlaydi
        # asosiy category larga yoki sub category larga qaytaradi
        elif data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
                # print("parent:", parent_id)
            else:
                # print("No parent")
                parent_id = None

            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = send_category_buttons(categories, db_user['lang_id'])

            if parent_id:
                clicked_button = db.get_by_parent(category_id=parent_id)
                # print(clicked_button, "clicked button")

                if clicked_button and clicked_button['parent_id']:
                    buttons.append([
                        InlineKeyboardButton(text="Back", callback_data=f"category_back_{clicked_button['parent_id']}")
                    ])
                else:
                    buttons.append(
                        [InlineKeyboardButton(text="Back", callback_data="category_back")]
                    )
            try:
                if context.user_data.get("carts", {}):
                    buttons.append(
                        [InlineKeyboardButton(text=globals.BTN_BUY[db_user['lang_id']], callback_data='cart')])
            except Exception as e:
                logging.info("Xatolik:", e)
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

        # category_back bo'lmasa ishlaydi
        # eng asososiy category larni chiqaradi
        else:
            categories = db.get_categories_by_parent(parent_id=int(data_sp[1]))

            if categories:
                buttons = send_category_buttons(categories, db_user['lang_id'])
            else:
                products = db.get_products_by_category(int(data_sp[1]))
                buttons = send_product_buttons(products, db_user['lang_id'])

            clicked_button = db.get_by_parent(category_id=int(data_sp[1]))
            # print(clicked_button, "clicked button")

            if clicked_button and clicked_button['parent_id']:
                buttons.append(
                    [InlineKeyboardButton(text="Back", callback_data=f"category_back_{clicked_button['parent_id']}")]
                )
            else:
                buttons.append(
                    [InlineKeyboardButton(text="Back", callback_data="category_back")]
                )

            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

    elif data_sp[0] == 'cart':
        if len(data_sp) == 2 and data_sp[1] == 'clear':
            query.message.delete()
            context.user_data.pop('carts')
            categories = db.get_categories_by_parent()
            buttons = send_category_buttons(categories, db_user['lang_id'])

            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=globals.TEXT_CHOOSE_CATEGORY[db_user['lang_id']],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

        elif len(data_sp) == 2 and data_sp[1] == 'back':
            categories = db.get_categories_by_parent()
            buttons = send_category_buttons(categories, db_user['lang_id'])
            buttons.append(
                [InlineKeyboardButton(text=globals.BTN_BUY[db_user['lang_id']], callback_data='cart')])
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

        else:
            buttons = [
                [InlineKeyboardButton(text=globals.BTN_ORDER_TO_GET[db_user['lang_id']], callback_data="order"),
                 InlineKeyboardButton(text=globals.BTN_EMPTY_BASKET[db_user['lang_id']], callback_data="cart_clear")],
                [InlineKeyboardButton(text="Back", callback_data="cart_back")]
            ]
            query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

    elif data_sp[0] == "order":
        if len(data_sp) > 1 and data_sp[1] == "payment":
            context.user_data['payment_type'] = (data_sp[2])
            buttons = [
                [InlineKeyboardButton(text=globals.BTN_DELIVERY[db_user['lang_id']], callback_data="order_type_1"),
                 InlineKeyboardButton(text=globals.BTN_TAKE_AWAY[db_user['lang_id']], callback_data="order_type_2")]
            ]
            query.message.edit_reply_markup(InlineKeyboardMarkup(inline_keyboard=buttons))

        elif len(data_sp) > 1 and data_sp[1] == "type":
            context.user_data['order_type'] = int(data_sp[2])
            if int(data_sp[2]) == 1:
                query.message.delete()
                query.message.reply_text(
                    text=globals.SEND_LOCATION[db_user['lang_id']],
                    reply_markup=ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text=globals.SEND_LOCATION[db_user['lang_id']], request_location=True)]
                    ], resize_keyboard=True, one_time_keyboard=True)
                )
            else:
                location_handler(update, context)

        else:
            buttons = [
                [InlineKeyboardButton(text=globals.BTN_CASH_MONEY[db_user['lang_id']], callback_data="order_payment_1"),
                 InlineKeyboardButton(text=globals.BTN_CARD[db_user['lang_id']], callback_data="order_payment_2")]
            ]
            query.message.edit_reply_markup(InlineKeyboardMarkup(inline_keyboard=buttons))
