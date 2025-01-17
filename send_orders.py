from database import Database
from config import DATA_BASE
from datetime import datetime
import globals
import logging

db = Database(DATA_BASE)


def send_user_all_orders(context, db_user):
    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
    orders = db.get_user_all_orders(db_user['chat_id'], lang_code)

    send_orders = []
    total_price = 0

    compare_order_id = int()
    for i in range(len(orders)):
        if compare_order_id == orders[i]['id']:
            send_orders[-1] += f"{orders[i]['amount']} x {orders[i][f'c_name_{lang_code}']} {orders[i][f'p_name_{lang_code}']}\n"
            total_price += int(orders[i]['all'])
        else:
            if compare_order_id != orders[i]['id'] and len(send_orders) > 0 and compare_order_id < orders[i]['id']:
                try:
                    send_orders[-1] += f"\n{globals.ALL[db_user['lang_id']]} {total_price} {globals.SUM[db_user['lang_id']]}"
                    total_price = 0
                except Exception as e:
                    logging.info(f"Xatolik: {e}")
            total_price += int(orders[i]['all'])
            format_date = datetime.strptime(orders[i]['created_at'], "%Y-%m-%d %H:%M:%S.%f")
            datetime_without_microseconds = format_date.replace(microsecond=0)
            date = datetime_without_microseconds.strftime("%Y-%m-%d %H:%M:%S")

            pay_type = globals.BTN_CASH_MONEY[db_user['lang_id']] if orders[i]['payment_type'] == '1' else globals.BTN_CARD[db_user['lang_id']] if orders[i]['payment_type'] == '2' else ""
            or_type = globals.BTN_DELIVERY[db_user['lang_id']] if orders[i]['order_type'] == 1 else globals.BTN_TAKE_AWAY[db_user['lang_id']] if orders[i]['order_type'] == 2 else ""

            if orders[i]['address']:
                address = "📍 <b>" + globals.TEXT_ADDRESS[db_user['lang_id']] + "</b> " + orders[i]['address']
            else:
                company = db.get_company_info()
                our_ad = globals.SEND_OUR_LOCATION[db_user['lang_id']]
                address = f"📍 <b>{our_ad}</b> {company[f'name_{lang_code}']}, {company[f'address_{lang_code}']}"

            text = f"🆔 <b>{globals.TEXT_ORDER_ID[db_user['lang_id']]}</b> {orders[i]['id']}\n" + \
                   f"📆 <b>{globals.TEXT_DATE_TIME[db_user['lang_id']]}</b> {date}\n" + \
                   f"💰 <b>{globals.TEXT_PAYMENT_TYPE[db_user['lang_id']]}</b> {pay_type}\n" + \
                   f"📦 <b>{globals.TEXT_ORDER_TYPE[db_user['lang_id']]}</b> {or_type}\n" + \
                   f"{address}\n\n" + \
                   f"📥 <b>{globals.ORDER[db_user['lang_id']]}:</b>\n\n" + \
                   f"{orders[i]['amount']} x {orders[i][f'c_name_{lang_code}']} {orders[i][f'p_name_{lang_code}']}\n"
            send_orders.append(text)
            compare_order_id = int(orders[i]['id'])
    send_orders[-1] += f"\n{globals.ALL[db_user['lang_id']]} {total_price} {globals.SUM[db_user['lang_id']]}"

    return send_orders
