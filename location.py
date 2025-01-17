from database import Database
from config import DATA_BASE, ADMIN_ID
from methods import send_main_menu
from geo_name import get_location_address
import datetime
import globals
import logging

db = Database(DATA_BASE)


def location_handler(update, context):
    db_user = context.user_data['db_user']
    payment_type = context.user_data.get('payment_type', None)
    order_type = context.user_data.get('order_type', None)

    try:
        location = update.message.location
        address = get_location_address(location)
    except Exception as e:
        logging.info(f"Xatolik: {e}")
        location = None
        address = None

    db.create_order(db_user['id'], context.user_data.get('carts', {}), payment_type, order_type, location, address)

    order = db.get_user_last_order_by_orders(db_user['id'])
    order_id = order['id']
    format_date = datetime.datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S.%f")
    datetime_without_microseconds = format_date.replace(microsecond=0)
    date = datetime_without_microseconds.strftime("%Y-%m-%d %H:%M:%S")

    if context.user_data.get('carts', {}):
        carts = context.user_data['carts']
        text = "\n"
        lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
        total_price = 0

        for cart, val in carts.items():
            product = db.get_product_for_cart(int(cart))
            text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
            total_price += val * product['price']

        text += f"\n{globals.ALL[db_user['lang_id']]} {total_price} {globals.SUM[db_user['lang_id']]}"

        pay_type = globals.BTN_CASH_MONEY[db_user['lang_id']] if payment_type == '1' else globals.BTN_CARD[db_user['lang_id']] if payment_type == '2' else ""
        or_type = globals.BTN_DELIVERY[db_user['lang_id']] if order_type == 1 else globals.BTN_TAKE_AWAY[db_user['lang_id']] if order_type == 2 else ""

        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"<b>Yangi buyurtma:</b>\n\n"
                 f"🆔 <b>Buyurtma raqami:</b> {order_id}\n"
                 f"👤 <b>Ism-familiya:</b> {db_user['first_name']} {db_user['last_name']}\n"
                 f"📞 <b>Telefon raqam:</b> {db_user['phone_number']}\n"
                 f"💰 <b>To'lov turi: {pay_type}</b>\n"
                 f"📦 <b>Buyurtma turi: {or_type}</b>\n"
                 f"📆 <b>Sana-vaqt: {date}</b>\n\n"
                 f"📥 <b>Buyurtma:</b>\n"
                 f"{text}",
            parse_mode="HTML"
        )

        if location:
            context.bot.send_location(
                chat_id=ADMIN_ID,
                latitude=location.latitude,
                longitude=location.longitude
            )

        if address:
            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=address
            )

        if order_type == 1:
            context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=f"🆔 <b>{globals.TEXT_ORDER_ID[db_user['lang_id']]}</b> {order_id}\n"
                     f"📆 <b>{globals.TEXT_DATE_TIME[db_user['lang_id']]}</b> {date}\n"
                     f"💰 <b>{globals.TEXT_PAYMENT_TYPE[db_user['lang_id']]}</b> {pay_type}\n"
                     f"📦 <b>{globals.TEXT_ORDER_TYPE[db_user['lang_id']]}</b> {or_type}\n"
                     f"📍 <b>{globals.TEXT_ADDRESS[db_user['lang_id']]}</b> {address}\n\n"
                     f"📥 <b>{globals.ORDER[db_user['lang_id']]}:</b>\n"
                     f"{text}",
                parse_mode="HTML"
            )
        else:
            company = db.get_company_info()
            our_ad = globals.SEND_OUR_LOCATION[db_user['lang_id']]
            address = f"📍 <b>{our_ad}</b> {company[f'name_{lang_code}']}, {company[f'address_{lang_code}']}"
            latitude, longitude = company['latitude'], company['longitude']
            context.bot.send_message(
                chat_id=db_user['chat_id'],
                text=f"🆔 <b>{globals.TEXT_ORDER_ID[db_user['lang_id']]}</b> {order_id}\n"
                     f"📆 <b>{globals.TEXT_DATE_TIME[db_user['lang_id']]}</b> {date}\n"
                     f"💰 <b>{globals.TEXT_PAYMENT_TYPE[db_user['lang_id']]}</b> {pay_type}\n"
                     f"📦 <b>{globals.TEXT_ORDER_TYPE[db_user['lang_id']]}</b> {or_type}\n"
                     f"{address}\n\n"
                     f"📥 <b>{globals.ORDER[db_user['lang_id']]}:</b>\n"
                     f"{text}",
                parse_mode="HTML"
            )
            context.bot.send_location(
                chat_id=db_user['chat_id'],
                latitude=latitude,
                longitude=longitude
            )
        context.user_data.pop("carts")
        send_main_menu(context, db_user['chat_id'], db_user['lang_id'])
