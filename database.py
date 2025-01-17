from datetime import datetime
import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(database=db_name, check_same_thread=False)
        self.cur = self.conn.cursor()

    def create_user(self, chat_id):
        self.cur.execute("""INSERT INTO Users(chat_id) VALUES (?);""", (chat_id,))
        self.conn.commit()

    def update_user_data(self, chat_id, key, value):
        self.cur.execute(f"""UPDATE Users SET {key} = ? WHERE chat_id = ?;""", (value, chat_id))
        self.conn.commit()

    def get_user_by_chat_id(self, chat_id):
        self.cur.execute("""SELECT * FROM Users WHERE chat_id = ?;""", (chat_id,))
        user = dict_fetchone(self.cur)
        return user

    def get_categories_by_parent(self, parent_id=None):
        if parent_id:
            self.cur.execute("""SELECT * FROM Category WHERE parent_id = ?;""", (parent_id,))
        else:
            self.cur.execute("""SELECT * FROM Category WHERE parent_id is NULL;""")

        categories = dict_fetchall(self.cur)
        return categories

    def get_by_parent(self, category_id):
        self.cur.execute("""SELECT parent_id FROM Category WHERE id = ?;""", (category_id,))
        category = dict_fetchone(self.cur)
        return category

    def get_products_by_category(self, category_id):
        self.cur.execute("""SELECT * FROM Product WHERE category_id = ?;""", (category_id,))
        products = dict_fetchall(self.cur)
        return products

    def get_product_by_id(self, product_id):
        self.cur.execute("""SELECT * FROM Product WHERE id = ?;""", (product_id,))
        product = dict_fetchone(self.cur)
        return product

    def get_product_for_cart(self, product_id):
        self.cur.execute("""SELECT p.*, c.name_uz as cat_name_uz, c.name_ru as cat_name_ru, c.name_en as cat_name_en
        FROM 'Product' p INNER JOIN 'Category' c ON p.category_id = c.id WHERE p.id = ?;""", (product_id,))

        product = dict_fetchone(self.cur)
        return product

    def create_order(self, user_id, products, payment_type, order_type, location=None, address=None):
        if location and address:
            self.cur.execute(
                """INSERT INTO 'Order' (user_id, status, created_at, payment_type, latitude, longitude, order_type, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                (user_id, 1, datetime.now(), payment_type, location.latitude, location.longitude, order_type, address))
            self.conn.commit()
        else:
            self.cur.execute(
                """INSERT INTO 'Order' (user_id, status, created_at, payment_type, order_type)
                    VALUES (?, ?, ?, ?, ?);""",
                (user_id, 1, datetime.now(), payment_type, order_type))
            self.conn.commit()

        self.cur.execute("""SELECT MAX(id) as last_order FROM 'Order' WHERE user_id = ?;""", (user_id,))
        last_order = dict_fetchone(self.cur)['last_order']

        for key, val in products.items():
            self.cur.execute("""INSERT INTO 'OrderProduct' (order_id, product_id, amount, created_at)
                                VALUES (?, ?, ?, ?);""",
                             (last_order, int(key), int(val), datetime.now()))
        self.conn.commit()

    def get_company_info(self):
        self.cur.execute("""SELECT * FROM Company WHERE id = ?;""", (1,))
        company = dict_fetchone(self.cur)
        return company

    def get_user_last_order_by_orders(self, user_id):
        self.cur.execute("""SELECT MAX(id) as last_order FROM 'Order' WHERE user_id = ?;""", (user_id,))
        last_order = dict_fetchone(self.cur)['last_order']

        self.cur.execute("""SELECT id, created_at FROM 'Order' WHERE id = ?;""", (last_order,))
        order = dict_fetchone(self.cur)
        return order

    def get_user_all_orders(self, chat_id, lang_code):
        self.cur.execute(
            f"""SELECT o.id, o.created_at, o.payment_type, o.order_type, o.address, op.amount, p.name_{lang_code} p_name_{lang_code}, c.name_{lang_code} c_name_{lang_code}, p.price * op.amount as "all"
                            FROM "OrderProduct" as op
                            INNER JOIN "Product" as p ON op.product_id = p.id
                            INNER JOIN "Category" as c ON p.category_id = c.id
                            INNER JOIN "Order" as o ON op.order_id = o.id
                            INNER JOIN Users as u ON o.user_id = u.id
                            WHERE op.order_id IN (SELECT id FROM "Order" WHERE user_id IN (SELECT id FROM Users WHERE chat_id = ?));""",
            (chat_id,))
        orders = dict_fetchall(self.cur)
        return orders

    def create_suggestion(self, chat_id, message, status):
        self.cur.execute("""INSERT INTO Suggestions (user_id, message, status, created_at) VALUES (?, ?, ?, ?);""",
                         (chat_id, message, status, datetime.now()))
        self.conn.commit()

    def update_suggestion(self, suggestion_id, status):
        self.cur.execute("""UPDATE Suggestions SET status = ? WHERE id = ?;""", (status, suggestion_id))
        self.conn.commit()


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
